import click

from lizzy.cli import BaseCommand
from lizzy.config import get_setting
from lizzy.gitlab import setup_gitlab
import re


class GitlabUpdateImageOfContainerCommand(BaseCommand):
    """Command to create a config file if it does not exist, or open it in vim if it does."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def gitlab_update_image_of_container():
            """Update the image of a container in a GitLab CI/CD pipeline."""
            components = get_setting("gitlab.components")
            environments = get_setting("gitlab.environments")
            components = components if components else []
            if not components:
                click.echo("❌ No components found in the configuration.", err=True)
                return
            click.Choice([component["name"] for component in components])
            component_name = click.prompt(
                "Enter the component name",
                type=click.Choice([component["name"] for component in components]),
            )
            tag = click.prompt("Enter the new image (e.g., myimage:latest)")
            click.Choice(environments)
            environment = click.prompt(
                "Enter the environment",
                type=click.Choice(environments),
            )
            component = next(
                (c for c in components if c["name"] == component_name), None
            )
            if not component:
                click.echo(
                    f"❌ Component '{component_name}' not found in the configuration.",
                    err=True,
                )
                return
            if "image_tag_locations" not in component:
                click.echo(
                    f"❌ Component '{component_name}' is missing 'image_tag_locations' in the configuration.",
                    err=True,
                )
                return

            if len(component["image_tag_locations"]) < 2:
                path = component["image_tag_locations"][0]["path"].replace(
                    "{env}", environment
                )
            else:
                click.Choice([loc["name"] for loc in component["image_tag_locations"]])
                location_name = click.prompt(
                    "Enter the location name",
                    type=click.Choice(
                        [loc["name"] for loc in component["image_tag_locations"]]
                    ),
                )
                path = next(
                    (
                        loc["path"].replace("{env}", environment)
                        for loc in component["image_tag_locations"]
                        if loc["name"] == location_name
                    ),
                    None,
                )
                if not path:
                    click.echo(
                        f"❌ Location '{location_name}' not found in the configuration.",
                        err=True,
                    )
                    return
            message = f"Updating component '{component_name}' to use image '{tag}' in environment '{environment}' at path '{path}'"
            click.echo(message)
            username = get_setting("gitlab.username")
            email = get_setting("gitlab.email")

            gl = setup_gitlab()
            project = gl.projects.get(component["project_name_with_namespace"])

            # Verify file exists before attempting to update
            try:
                file = project.files.get(file_path=path, ref=component["branch"])
            except Exception as e:
                click.echo(
                    f"❌ Error: File not found at path '{path}' on branch '{component['branch']}'",
                    err=True,
                )
                click.echo(f"   GitLab error: {str(e)}", err=True)

                # Try to list files in the repository to help debug
                try:
                    click.echo(f"\n🔍 Searching for files in the repository...")
                    tree = project.repository_tree(
                        ref=component["branch"], recursive=True, per_page=100
                    )

                    # Filter for .tf files
                    tf_files = [
                        item["path"] for item in tree if item["path"].endswith(".tf")
                    ]

                    if tf_files:
                        click.echo(
                            f"\n📁 Found {len(tf_files)} Terraform files in the repository:"
                        )
                        for tf_file in tf_files[:20]:  # Show first 20
                            click.echo(f"   - {tf_file}")
                        if len(tf_files) > 20:
                            click.echo(f"   ... and {len(tf_files) - 20} more")
                    else:
                        click.echo("   No .tf files found in the repository")
                except Exception as tree_error:
                    click.echo(
                        f"   Could not list repository files: {str(tree_error)}",
                        err=True,
                    )

                return

            terraform_module = file.decode().decode("utf-8")

            # Check if the pattern exists in the file
            if not re.search(r'image_version\s*=\s*".*"', terraform_module):
                click.echo(
                    f"⚠️  Warning: Pattern 'image_version = \"...\"' not found in {path}",
                    err=True,
                )
                click.echo(
                    f"   The file may not contain the expected Terraform variable.",
                    err=True,
                )

                # Show a preview of the file content
                lines = terraform_module.split("\n")[:20]
                click.echo(f"\n📄 File preview (first 20 lines):")
                for i, line in enumerate(lines, 1):
                    click.echo(f"   {i}: {line}")

                if not click.confirm("\nDo you want to continue anyway?"):
                    click.echo("Update cancelled.")
                    return

            updated_module = re.sub(
                r'image_version\s*=\s*".*"',
                f'image_version = "{tag}"',
                terraform_module,
            )

            commit_data = {
                "branch": component["branch"],
                "commit_message": message,
                "actions": [],
                "author_name": username,
                "author_email": email,
            }

            commit_data["actions"].append(
                {
                    "action": "update",
                    "file_path": path,
                    "content": updated_module,
                }
            )

            try:
                project.commits.create(commit_data)
                click.echo("✅ Component updated successfully.")
                click.echo(f"   Commit message: {message}")
            except Exception as commit_error:
                click.echo(f"❌ Error creating commit: {str(commit_error)}", err=True)
                return
