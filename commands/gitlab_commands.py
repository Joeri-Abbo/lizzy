import click

from lizzy.cli import BaseCommand


class GitlabCommands(BaseCommand):
    """Manage GitLab operations."""

    @staticmethod
    def register(command_group):
        @command_group.group()
        def gitlab():
            """Manage GitLab operations: develop-to-main, main-to-develop, merge-approved, remove-merged-branches, update-image-of-container"""
            pass

        @gitlab.command(name="develop-to-main")
        def develop_to_main():
            """Create merge requests to switch from develop to main branch."""
            GitlabCommands._develop_to_main()

        @gitlab.command(name="main-to-develop")
        def main_to_develop():
            """Create merge requests to switch from main to develop branch."""
            GitlabCommands._main_to_develop()

        @gitlab.command(name="merge-approved")
        def merge_approved():
            """Merge all approved merge requests from my user."""
            GitlabCommands._merge_approved()

        @gitlab.command(name="remove-merged-branches")
        def remove_merged_branches():
            """Remove all merged branches in GitLab."""
            GitlabCommands._remove_merged_branches()

        @gitlab.command(name="update-image-of-container")
        def update_image_of_container():
            """Update the image of a container in a GitLab CI/CD pipeline."""
            GitlabCommands._update_image_of_container()

        # Register individual commands that show in main help with space syntax
        @command_group.command(name="gitlab develop-to-main")
        def gitlab_develop_to_main_main():
            """Create merge requests to switch from develop to main branch."""
            GitlabCommands._develop_to_main()

        @command_group.command(name="gitlab main-to-develop")
        def gitlab_main_to_develop_main():
            """Create merge requests to switch from main to develop branch."""
            GitlabCommands._main_to_develop()

        @command_group.command(name="gitlab merge-approved")
        def gitlab_merge_approved_main():
            """Merge all approved merge requests from my user."""
            GitlabCommands._merge_approved()

        @command_group.command(name="gitlab remove-merged-branches")
        def gitlab_remove_merged_branches_main():
            """Remove all merged branches in GitLab."""
            GitlabCommands._remove_merged_branches()

        @command_group.command(name="gitlab update-image-of-container")
        def gitlab_update_image_of_container_main():
            """Update the image of a container in a GitLab CI/CD pipeline."""
            GitlabCommands._update_image_of_container()

    @staticmethod
    def _develop_to_main():
        """Create merge requests to switch from develop to main branch."""
        from lizzy.helpers.gitlab import develop_to_main
        develop_to_main()
        click.echo("Switched GitLab branches from develop to main.")

    @staticmethod
    def _main_to_develop():
        """Create merge requests to switch from main to develop branch."""
        from lizzy.helpers.gitlab import main_to_develop
        main_to_develop()
        click.echo("Switched GitLab branches from main to develop.")

    @staticmethod
    def _merge_approved():
        """Merge all approved merge requests from my user."""
        from lizzy.helpers.gitlab import fetch_approved_merge_requests
        fetch_approved_merge_requests()
        click.echo("Merged approved pull requests from GitLab.")

    @staticmethod
    def _remove_merged_branches():
        """Remove all merged branches in GitLab."""
        from lizzy.helpers.gitlab import remove_merged_branches
        remove_merged_branches()
        click.echo("Removed merged branches from GitLab.")

    @staticmethod
    def _update_image_of_container():
        """Update the image of a container in a GitLab CI/CD pipeline."""
        from lizzy.helpers.config import get_setting
        from lizzy.helpers.gitlab import setup_gitlab
        
        components = get_setting("gitlab.components")
        environments = get_setting("gitlab.environments")
        components = components if components else []
        if not components:
            click.echo("No components found in configuration.")
            return

        gl = setup_gitlab()
        
        # Get user inputs
        component_name = click.prompt(
            "Select a component",
            type=click.Choice([comp["name"] for comp in components]),
            show_choices=True,
        )
        
        selected_component = next(comp for comp in components if comp["name"] == component_name)
        
        environment = click.prompt(
            f"Select an environment for {component_name}",
            type=click.Choice(environments),
            show_choices=True,
        )
        
        new_image = click.prompt(f"Enter the new image for {component_name} in {environment}")
        
        # Update the component image
        GitlabCommands._process_gitlab_update(gl, selected_component, environment, new_image)
        
        click.echo(f"Updated {component_name} image to {new_image} in {environment} environment.")

    @staticmethod
    def _process_gitlab_update(gl, component, environment, new_image):
        """Process the GitLab repository update for a component."""
        import re
        
        try:
            project = gl.projects.get(component["project_id"])
            branch_name = f"update-{component['name']}-{environment}"
            
            # Create or get branch
            try:
                project.branches.create({"branch": branch_name, "ref": "main"})
            except Exception:
                project.branches.get(branch_name)
            
            # Update the file
            file_path = component["file_path"].format(environment=environment)
            
            try:
                file = project.files.get(file_path=file_path, ref=branch_name)
                content = file.decode()
                
                # Update image in the content
                pattern = rf"({re.escape(component['image_pattern'])}):.*"
                new_content = re.sub(pattern, f"\\1:{new_image}", content.decode('utf-8'))
                
                file.content = new_content
                file.save(branch=branch_name, commit_message=f"Update {component['name']} to {new_image}")
                
                # Create merge request
                mr = project.mergerequests.create({
                    'source_branch': branch_name,
                    'target_branch': 'main',
                    'title': f"Update {component['name']} to {new_image} in {environment}",
                    'description': f"Automated update of {component['name']} image to {new_image}"
                })
                
                click.echo(f"Created merge request: {mr.web_url}")
                
            except Exception as e:
                click.echo(f"Error updating file: {e}")
                
        except Exception as e:
            click.echo(f"Error processing GitLab update: {e}")