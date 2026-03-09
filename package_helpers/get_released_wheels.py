import zipfile, tempfile, os, shutil, csv, hashlib, base64, subprocess, sys, requests

def download_release_assets(tag, output_dir, owner="StemVibrations", repo="Kratos"):
    OWNER = owner
    REPO = repo
    TAG = tag

    OUTPUT_DIR = output_dir

    # Optional: GitHub token (avoid rate limits on public API)
    # Create a personal access token and set GITHUB_TOKEN env var
    TOKEN = os.getenv("GITHUB_TOKEN")

    # ——————————————————————————————
    # End configuration
    # ——————————————————————————————

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Headers for API call (include token if provided)
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    # Step 1 — Get the release metadata by tag
    api_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{TAG}"
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    release = response.json()

    assets = release.get("assets", [])
    if not assets:
        print("No assets found for release", TAG)
        exit(0)

    # Step 2 — Download each asset
    for asset in assets:
        name = asset["name"]
        download_url = asset["browser_download_url"]
        print(f"Downloading {name} …")

        out_path = os.path.join(OUTPUT_DIR, name)

        # Stream the download so we don't load the entire file at once
        with requests.get(download_url, stream=True) as dl:
            dl.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in dl.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"Saved {name} to {out_path}")

    print("All assets downloaded!")

def clean_linux_wheels(wheel_dir, new_wheels_dir, kratos_version, cpython_versions, platform_tag):
    """
    Clean the Linux wheels by removing .pyc files and unnecessary shared libraries, stripping symbols,
    and patching rpath.

    This is required to reduce the size of the linux wheels.
    """
    if sys.platform != "linux":
        raise RuntimeError("This script is intended to be run on Linux systems.")

    GLOBAL_RPATH = (
        "$ORIGIN:"
        "$ORIGIN/../libs:"
        "$ORIGIN/../../stemkratosmultiphysics.libs:"
        "$ORIGIN/../../stemkratosstructuralmechanicsapplication.libs:"
        "$ORIGIN/../../stemkratoslinearsolversapplication.libs:"
        "$ORIGIN/../../stemkratosgeomechanicsapplication.libs:"
        "$ORIGIN/../../stemkratosrailwayapplication.libs"
    )

    stemrailwayapplication_data = {"wheel_name": "stemkratosrailwayapplication",
                                   "lib_dependencies": ["libKratosCore", "libKratosLinearSolversCore",
                                                        "libKratosStructuralMechanicsCore",
                                                        "libKratosGeoMechanicsCore"]}

    stemgeomechanicsapplication_data = {"wheel_name": "stemkratosgeomechanicsapplication",
                                        "lib_dependencies": ["libKratosCore", "libKratosLinearSolversCore",
                                                             "libKratosStructuralMechanicsCore"]}
    stemstructuralmechanicsapplication_data = {"wheel_name": "stemkratosstructuralmechanicsapplication",
                                               "lib_dependencies": ["libKratosCore", "libKratosLinearSolversCore"]}

    stemlinearsolversapplication_data = {"wheel_name": "stemkratoslinearsolversapplication",
                                         "lib_dependencies": ["libKratosCore"]}

    stemkratoscore_data = {"wheel_name": "stemkratosmultiphysics",
                           "lib_dependencies": []}

    all_wheels_data = [stemrailwayapplication_data, stemgeomechanicsapplication_data,
                       stemstructuralmechanicsapplication_data, stemlinearsolversapplication_data, stemkratoscore_data]

    current_dir = os.getcwd()
    os.chdir(wheel_dir)
    for data in all_wheels_data:
        for cpython_version in cpython_versions:
            base_wheel_name = data["wheel_name"]
            full_wheel_name = f"{base_wheel_name}-{kratos_version}-{cpython_version}-{platform_tag}.whl"

            REMOVE_LIBS = data["lib_dependencies"]

            def sha256_file(p):
                h = hashlib.sha256()
                with open(p, 'rb') as f:
                    for c in iter(lambda: f.read(8192), b''):
                        h.update(c)
                return "sha256=" + base64.urlsafe_b64encode(h.digest()).decode().rstrip("="), str(os.path.getsize(p))

            with tempfile.TemporaryDirectory() as tmp:

                with zipfile.ZipFile(full_wheel_name) as z:
                    z.extractall(tmp)

                dist = [d for d in os.listdir(tmp) if d.endswith(".dist-info")][0]
                record = os.path.join(tmp, dist, "RECORD")

                removed = set()

                for root, dirs, files in os.walk(tmp):
                    for f in files:
                        p = os.path.join(root, f)
                        rel = os.path.relpath(p, tmp)

                        if f.endswith(".pyc"):
                            os.remove(p)
                            removed.add(rel)

                        if rel.startswith(f"{base_wheel_name}.libs"):
                            if any(f.startswith(prefix) and f.endswith(".so") for prefix in REMOVE_LIBS):
                                os.remove(p)
                                removed.add(rel)

                        if f.endswith(".so") and os.path.exists(p):
                            # strip symbols
                            subprocess.run(["strip", "--strip-unneeded", p], check=False)

                            # patch rpath
                            subprocess.run(
                                ["patchelf", "--set-rpath", GLOBAL_RPATH, p],
                                check=False
                            )

                    if "__pycache__" in dirs:
                        shutil.rmtree(os.path.join(root, "__pycache__"))

                rows = []
                with open(record) as f:
                    for r in csv.reader(f):
                        rows.append(r)

                new = []
                for path, _, _ in rows:

                    if path in removed:
                        continue

                    full = os.path.join(tmp, path)

                    if path.endswith("RECORD"):
                        new.append([path, "", ""])
                    elif os.path.exists(full):
                        h, s = sha256_file(full)
                        new.append([path, h, s])

                with open(record, "w", newline="") as f:
                    csv.writer(f).writerows(new)

                # Check if new_wheels_dir is absolute, if not make it relative to current_dir
                if not os.path.isabs(new_wheels_dir):   
                    new_wheels_dir = os.path.join(current_dir, new_wheels_dir)

                if not os.path.exists(new_wheels_dir):
                    os.mkdir(new_wheels_dir)
                out = os.path.join(new_wheels_dir, full_wheel_name)

                with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
                    for root, _, files in os.walk(tmp):
                        for f in files:
                            full = os.path.join(root, f)
                            z.write(full, os.path.relpath(full, tmp))
    print("Created:", out)
    os.chdir(current_dir)


def move_windows_wheels(source_dir, target_dir, windows_platform_tag):
    for f in os.listdir(source_dir):
        if f.endswith(f"{windows_platform_tag}.whl"):
            shutil.move(os.path.join(source_dir, f), os.path.join(target_dir, f))
            print(f"Moved {f} to {target_dir}")

def move_platform_independent_wheels(source_dir, target_dir):
    for f in os.listdir(source_dir):
        if f.endswith("-any.whl"):
            shutil.move(os.path.join(source_dir, f), os.path.join(target_dir, f))
            print(f"Moved {f} to {target_dir}")

def cleanup(dir):
    for f in os.listdir(dir):
        if f.endswith(".whl"):
            os.remove(os.path.join(dir, f))
            print(f"Removed {f} from {dir}")

if __name__ == "__main__":

    if sys.platform != "linux":
        raise RuntimeError("This script is intended to be run on Linux systems, "
                           "as this is required to clean the linux wheels.")

    release_tag = "release1.3.0"  # exact tag name

    kratos_version = "10.3.1.5"
    cpython_versions = ["cp310-cp310", "cp311-cp311", "cp312-cp312"]
    linux_platform_tag = "manylinux_2_34_x86_64"
    windows_platform_tag = "win_amd64"

    download_dir = "downloaded_wheels"
    cleaned_dir = "dist"

    download_release_assets(release_tag, download_dir)
    clean_linux_wheels(download_dir, cleaned_dir, kratos_version, cpython_versions, linux_platform_tag)
    move_windows_wheels(download_dir, cleaned_dir, windows_platform_tag)
    move_platform_independent_wheels(download_dir, cleaned_dir)

    cleanup(download_dir)



