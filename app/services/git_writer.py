from pathlib import Path
from git import Repo
from datetime import datetime
import os

GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", "/tmp/gitops-repo")


def commit_manifest(tenant_id: str, resource_type: str, resource_name: str, manifest_content: str, branch: str = "main") -> str:
    repo = Repo(GIT_REPO_PATH)
    if repo.is_dirty():
        repo.git.reset("--hard")

    repo.git.checkout(branch)

    dest_dir = Path(GIT_REPO_PATH) / tenant_id / resource_type
    dest_dir.mkdir(parents=True, exist_ok=True)
    file_path = dest_dir / f"{resource_name}.yaml"
    file_path.write_text(manifest_content)

    repo.index.add([str(file_path)])
    commit_msg = f"{tenant_id}: {resource_type} {resource_name} updated @ {datetime.utcnow().isoformat()}"
    repo.index.commit(commit_msg)
    repo.git.push("origin", branch)
    return commit_msg
