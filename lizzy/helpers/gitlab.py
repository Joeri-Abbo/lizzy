import click
import gitlab

from lizzy.helpers.config import get_setting


def setup_gitlab() -> gitlab.Gitlab:
    """Set up and return a GitLab connection using the API token from the config."""
    api_token = get_setting("gitlab.api_token")
    if not api_token:
        raise ValueError("GitLab API token is not set in the configuration.")
    gl = gitlab.Gitlab("https://gitlab.com", private_token=api_token)
    return gl


def develop_to_main() -> None:
    """Switch all specified GitLab repositories from 'develop' branch to 'main' branch."""

    components = get_setting("gitlab.components")
    components = components if components else []
    gl = setup_gitlab()
    for component in components:
        try:
            print(f"Processing component: {component['name']}")
            project = gl.projects.get(component["project_name_with_namespace"])

            merge_request = project.mergerequests.create(
                {
                    "source_branch": "develop",
                    "target_branch": "main",
                    "title": "Develop to main",
                }
            )
            print(f"Merge request created: {merge_request.web_url}")
        except Exception as e:
            print(f"Failed to create merge request for {component['name']}: {e}")


def main_to_develop() -> None:
    """Switch all specified GitLab repositories from 'main' branch to 'develop' branch."""

    components = get_setting("gitlab.components")
    components = components if components else []
    gl = setup_gitlab()
    for component in components:
        try:
            print(f"Processing component: {component['name']}")
            project = gl.projects.get(component["project_name_with_namespace"])

            merge_request = project.mergerequests.create(
                {
                    "source_branch": "main",
                    "target_branch": "develop",
                    "title": "Main to Develop",
                }
            )
            print(f"Merge request created: {merge_request.web_url}")
        except Exception as e:
            print(f"Failed to create merge request for {component['name']}: {e}")


def remove_merged_branches() -> None:
    """Remove all merged branches in specified GitLab repositories."""
    gl = setup_gitlab()
    approval_group_id = get_setting("gitlab.approval_group_id")
    group = gl.groups.get(approval_group_id)

    projects = group.projects.list(include_subgroups=True, all=True)
    for project in projects:
        click.echo(f"Found project: {project.name}, scanning for merged branches...")
        proj = gl.projects.get(project.id)
        branches = proj.branches.list(all=True)

        for branch in branches:
            if branch.name not in ["main", "develop", "master"] and branch.merged:
                click.echo(f"Removing merged branch: {branch.name}")
                try:
                    proj.branches.delete(branch.name)
                except Exception as e:
                    click.echo(f"Failed to remove branch {branch.name}: {e}")


def fetch_approved_merge_requests(yolo: bool = False) -> None:
    """Fetch all approved merge requests from specified GitLab repositories."""

    gl = setup_gitlab()
    approval_group_id = get_setting("gitlab.approval_group_id")
    username = get_setting("gitlab.username")
    group = gl.groups.get(approval_group_id)

    projects = group.projects.list(include_subgroups=True, all=True)
    for project in projects:
        try:
            click.echo(f"Found project: {project.name}, scanning for approved MRs...")
            proj = gl.projects.get(project.id)
            merge_requests = proj.mergerequests.list(state="opened", all=True)
            if not merge_requests:
                click.echo(f"No open merge requests found for project: {project.name}")
                continue

            for mr in merge_requests:
                if mr.author["username"] != username:
                    click.echo(f"Skipping MR {mr.title} by {mr.author['username']}")
                    continue

                mr_detail = proj.mergerequests.get(mr.iid)
                pipelines = mr_detail.pipelines.list(per_page=1,get_all=True)

                if not pipelines:
                    click.echo(f"No pipelines for MR {mr.title}")
                    continue
                pipeline = pipelines[0]

                if pipeline.status != "success":
                    click.echo(f"MR {mr.title} has failed jobs, skipping")
                    continue

                approvals = mr_detail.approvals.get()

                success = False
                for approver in approvals.approved_by:
                    if approver["user"]["username"] != username:
                        success = True
                        click.echo(
                            f"MR {mr.title} approved by {approver['user']['username']} created by {mr.author['username']}"
                        )
                        break
                if success:
                    click.echo(f"Found approved merge request: {mr.title} ({mr.web_url})")
                    if yolo:
                        click.echo(f"Auto-merging MR {mr.title}")
                        mr_detail.merge()
                    else:
                        if input(f"Merge {mr.title}? (y/n): ").lower() == "y":
                            try:
                                mr_detail.merge()
                                click.echo(f"Merged MR: {mr.title}")
                            except Exception as e:
                                click.echo(f"Failed to merge MR {mr.title}: {e}")
        except Exception as e:
            click.echo(f"Error processing project {project.name}: {e}")
