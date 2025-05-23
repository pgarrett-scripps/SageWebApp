import streamlit as st
import platform
import requests
import tarfile
import os
import subprocess
import tempfile
import shutil
import zipfile
import pandas as pd


# Fill out params, save as json
# upload mzml.gz.tar(s) and fasta
# search
# download results as zip file
# show results

sage_files = {
    "linux_aarch64": "https://github.com/lazear/sage/releases/download/v0.14.7/sage-v0.14.7-aarch64-unknown-linux-gnu.tar.gz",
    "linux_x86_64": "https://github.com/lazear/sage/releases/download/v0.14.7/sage-v0.14.7-x86_64-unknown-linux-gnu.tar.gz",
}

# get system architecture
arch = platform.machine()
if arch == "x86_64":
    arch = "linux_x86_64"
elif arch == "aarch64":
    arch = "linux_aarch64"
else:
    st.error("Unsupported architecture. Please use x86_64 or aarch64.")


# download sage
def download_sage(arch):
    url = sage_files[arch]
    st.info(f"Downloading Sage from {url}...")

    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Download the tar file
            tar_path = os.path.join(tmp_dir, "sage.tar.gz")
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                st.error(f"Failed to download Sage: HTTP status {response.status_code}")
                return

            with open(tar_path, "wb") as f:
                f.write(response.content)

            # Extract the tar file
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=tmp_dir)

            # Find the extracted directory (should be sage-v*-arch-*-linux-gnu)
            extracted_dirs = [
                d
                for d in os.listdir(tmp_dir)
                if d.startswith("sage-v") and os.path.isdir(os.path.join(tmp_dir, d))
            ]
            if not extracted_dirs:
                st.error("Could not find extracted Sage directory")
                return

            extracted_dir = os.path.join(tmp_dir, extracted_dirs[0])

            # Create the sage directory in the current working directory
            sage_dir = os.path.join(os.getcwd(), "sage")
            os.makedirs(sage_dir, exist_ok=True)

            # Copy the sage executable and other files
            for file in os.listdir(extracted_dir):
                src = os.path.join(extracted_dir, file)
                dst = os.path.join(sage_dir, file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    if file == "sage":  # Make the sage executable actually executable
                        os.chmod(dst, 0o755)

            st.success("Sage downloaded and installed successfully")
    except Exception as e:
        st.error(f"Error downloading or extracting Sage: {str(e)}")


@st.cache_resource
def load_sage(arch):
    # Check if sage directory exists
    if not os.path.exists("sage"):
        download_sage(arch)

    # Update PATH and return sage executable path
    sage_dir = os.path.abspath("sage")
    os.environ["PATH"] += os.pathsep + sage_dir
    return os.path.join(sage_dir, "sage")  # Return the full path to the sage executable


sage_path = load_sage(arch)

with st.sidebar:

    # Replace the text outputs with more informative content
    st.title("Sage Proteomics Search Engine")
    st.info(f"Running on: {platform.system()} {arch}")

    try:
        result = subprocess.run(
            [sage_path, "--version"], capture_output=True, text=True
        )
        st.info(f"Sage version: {result.stdout.strip()}")
    except Exception as e:
        st.error(f"Failed to get Sage version: {str(e)}")

    fasta_file = st.file_uploader("Upload FASTA file", type=["fasta"])
    mzml_files = st.file_uploader(
        "Upload mzML files", type=["mzml", "mzml.gz"], accept_multiple_files=True
    )
    json_file = st.file_uploader("Upload JSON file", type=["json"])

    include_fragment_annotations = st.checkbox(
        "Include fragment annotations", value=True
    )
    output_type = st.selectbox("Output type", ["csv", "parquet"])
    search_name = st.text_input("Search name", value="sage_search")


if st.button("Run"):
    if fasta_file is None:
        st.error("Please upload a FASTA file")
        st.stop()
    if not mzml_files:
        st.error("Please upload at least one mzML file")
        st.stop()
    if not json_file:
        st.error("Please upload a JSON file or provide parameters")
        st.stop()

    # open tmp directory
    with tempfile.TemporaryDirectory(delete=False, dir=".") as tmp_dir:
        # Save the uploaded files to the temporary directory
        fasta_path = os.path.join(tmp_dir, fasta_file.name)
        with open(fasta_path, "wb") as f:
            f.write(fasta_file.getbuffer())

        mzml_paths = []
        for mzml_file in mzml_files:
            mzml_path = os.path.join(tmp_dir, mzml_file.name)
            with open(mzml_path, "wb") as f:
                f.write(mzml_file.getbuffer())
            mzml_paths.append(mzml_path)

        # Save the JSON file to the temporary directory
        json_path = os.path.join(tmp_dir, json_file.name)
        with open(json_path, "wb") as f:
            f.write(json_file.getbuffer())

        output_path = os.path.join(tmp_dir, "output")

        # Run the command

        command = [
            sage_path,
            json_path,
            "".join(mzml_paths),
            "--output_directory",
            output_path,
            "--fasta",
            fasta_path,
        ]
        if include_fragment_annotations:
            command.append("--annotate-matches")

        if output_type == "parquet":
            command.append("--parquet")

        with st.spinner("Running Sage..."):

            try:
                result = subprocess.run(command, capture_output=True, text=True)
                st.success("Sage completed successfully")
            except Exception as e:
                st.error(f"Failed to run Sage: {str(e)}")
                st.stop()

            with st.expander("Sage output", expanded=False):
                stdout_tab, stderr_tab = st.tabs(["stdout", "stderr"])
                with stdout_tab:
                    st.code(result.stdout, language="text", height=300)
                with stderr_tab:
                    st.code(result.stderr, language="text", height=300)

            # download results (zip file)
            zip_path = os.path.join(tmp_dir, f"{search_name}.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for root, dirs, files in os.walk(output_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, output_path))

                # save the output as log.txt
                stdout_log_path = os.path.join(output_path, "stdout.txt")
                with open(stdout_log_path, "w") as logf:
                    logf.write(result.stdout)

                stderr_log_path = os.path.join(output_path, "stderr.txt")
                with open(stderr_log_path, "w") as logf:
                    logf.write(result.stderr)

            with open(zip_path, "rb") as f:
                st.download_button(
                    label="Download results",
                    data=f,
                    file_name=f"{search_name}.zip",
                    mime="application/zip",
                    on_click="ignore",
                )

            # show the results (either tsv or parquet files)
            st.subheader("Results")
            results = os.listdir(output_path)
            for file in results:
                if file.endswith(".tsv"):
                    df = pd.read_csv(os.path.join(output_path, file), sep="\t")
                    st.dataframe(df)
                if file.endswith(".parquet"):
                    df = pd.read_parquet(os.path.join(output_path, file))
                    st.dataframe(df)
