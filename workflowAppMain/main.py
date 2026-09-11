from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from code2flow.engine import code2flow

LANG_EXTENSIONS = {
    "Python": "py",
}

DEFAULT_SCRIPTS = {
    "Python": '''def main():
    data = load_data()
    model = train_model(data)
    evaluate_model(model, data)
    save_pipeline(model)

def load_data():
    raw = fetch_raw_data()
    return preprocess(raw)

def fetch_raw_data():
    return "raw_data"

def preprocess(data):
    validate_schema(data)
    return "cleaned_data"

def validate_schema(data):
    pass

def train_model(data):
    features = extract_features(data)
    return fit_estimator(features)

def extract_features(data):
    return [1, 2, 3]

def fit_estimator(features):
    return "trained_model"

def evaluate_model(model, data):
    metrics = compute_metrics(model)
    log_metrics(metrics)

def compute_metrics(model):
    return {"accuracy": 0.95}

def log_metrics(metrics):
    pass

def save_pipeline(model):
    export_to_mlflow(model)

def export_to_mlflow(model):
    pass

if __name__ == "__main__":
    main()
''',
    "JavaScript": '''function main() {
    const raw = fetchRawData();
    const data = preprocess(raw);
    const model = trainModel(data);
    evaluateModel(model);
    exportWorkflow(model);
}

function fetchRawData() {
    return "raw";
}

function preprocess(raw) {
    validate(raw);
    return "cleaned";
}

function validate(d) {}

function trainModel(data) {
    const features = extractFeatures(data);
    return fit(features);
}

function extractFeatures(d) {
    return [1, 2, 3];
}

function fit(f) {
    return { name: "model" };
}

function evaluateModel(m) {
    calculateScore(m);
}

function calculateScore(m) {}

function exportWorkflow(m) {}

main();
''',
    "Ruby": '''def main
  data = load_data
  model = train_model(data)
  evaluate(model)
  save_model(model)
end

def load_data
  preprocess(fetch_raw)
end

def fetch_raw
  "raw"
end

def preprocess(raw)
  validate(raw)
  "cleaned"
end

def validate(d); end

def train_model(data)
  fit(extract_features(data))
end

def extract_features(data)
  [1, 2, 3]
end

def fit(features)
  "model"
end

def evaluate(model)
  score(model)
end

def score(model); end

def save_model(model); end

main
''',
    "PHP": '''<?php
function main() {
    $data = load_data();
    $model = train_model($data);
    evaluate_model($model);
    save_pipeline($model);
}

function load_data() {
    $raw = fetch_raw();
    return preprocess($raw);
}

function fetch_raw() {
    return "raw";
}

function preprocess($raw) {
    validate($raw);
    return "cleaned";
}

function validate($d) {}

function train_model($data) {
    $features = extract_features($data);
    return fit($features);
}

function extract_features($data) {
    return [1, 2, 3];
}

function fit($features) {
    return "model";
}

function evaluate_model($model) {
    score($model);
}

function score($model) {}

function save_pipeline($model) {}

main();
?>
''',
}


def clone_repo(repo_url: str, destination: Path) -> Path:
    """Clone a remote repository into a temporary directory."""
    subprocess.run(["git", "clone", "--depth", "1", repo_url, str(destination)], check=True)
    return destination


def generate_flowchart(
    source_paths: list[str] | str,
    hide_legend: bool = False,
    no_grouping: bool = False,
    no_trimming: bool = False,
    language: str | None = None,
) -> tuple[Path, Path, Path | None]:
    """Generate a DOT graph, PNG image, and SVG image for a repo or script path."""
    temp_dir = Path(tempfile.mkdtemp(prefix="code2flow_"))
    dot_output = temp_dir / "workflow.gv"
    png_output = temp_dir / "workflow.png"
    svg_output = temp_dir / "workflow.svg"

    code2flow(
        raw_source_paths=source_paths,
        output_file=str(dot_output),
        language=language,
        hide_legend=hide_legend,
        no_grouping=no_grouping,
        no_trimming=no_trimming,
    )

    # Render PNG
    subprocess.run(["dot", "-Tpng", str(dot_output), "-o", str(png_output)], check=True)

    # Render SVG
    try:
        subprocess.run(["dot", "-Tsvg", str(dot_output), "-o", str(svg_output)], check=True)
    except Exception:
        svg_output = None

    return dot_output, png_output, svg_output


st.set_page_config(
    page_title="Code2Flow Workflow Visualizer",
    page_icon="🔀",
    layout="wide",
)

st.title("🔀 Code2Flow Workflow Visualizer")
st.caption(
    "Create interactive workflow diagrams directly from code scripts (Script Taker), uploaded files, or Git repositories."
)

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Flowchart Options")
    hide_legend = st.checkbox("Hide Legend", value=False)
    no_grouping = st.checkbox("No Grouping (Flatten namespaces)", value=False)
    no_trimming = st.checkbox("No Trimming (Keep orphaned functions)", value=False)
    st.markdown("---")
    st.markdown("### Supported Languages")
    st.markdown("- **Python** (`.py`)")
    st.markdown("- **JavaScript** (`.js`, `.mjs`)")
    st.markdown("- **Ruby** (`.rb`)")
    st.markdown("- **PHP** (`.php`)")

input_mode = st.radio(
    "Select Input Mode:",
    ["📝 Script Taker (Paste Code)", "📂 Upload Script File"],
    horizontal=True,
)

script_text = ""
target_language = None
run_triggered = False

if input_mode == "📝 Script Taker (Paste Code)":
    st.subheader("Script Taker")
    st.write("Write or paste your script code below to generate its execution workflow.")

    col1, col2 = st.columns([1, 2])
    with col1:
        selected_lang = st.selectbox("Language", list(LANG_EXTENSIONS.keys()), index=0)
        target_language = LANG_EXTENSIONS[selected_lang]
    with col2:
        load_example = st.checkbox("Load Sample Workflow Script", value=True)

    default_value = DEFAULT_SCRIPTS.get(selected_lang, "") if load_example else ""
    script_text = st.text_area(
        f"Enter {selected_lang} Code:",
        value=default_value,
        height=320,
        placeholder=f"Paste your {selected_lang} script here...",
    )
    run_triggered = st.button("🚀 Generate Workflow from Script", type="primary")

elif input_mode == "📂 Upload Script File":
    st.subheader("Upload Script File")
    uploaded_file = st.file_uploader(
        "Upload a script (.py, .js, .mjs, .rb, .php)",
        type=["py", "js", "mjs", "rb", "php"],
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        try:
            script_text = file_bytes.decode("utf-8")
            ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
            target_language = ext if ext in ["py", "js", "rb", "php"] else None
            with st.expander("📄 View Uploaded Code Preview", expanded=False):
                st.code(script_text, language=ext if ext in ["py", "js", "rb", "php"] else "text")
        except UnicodeDecodeError:
            st.error("Uploaded file could not be decoded as text.")

    run_triggered = st.button("🚀 Generate Workflow from Uploaded File", type="primary")

else:
    st.subheader("Git Repo / Local Directory or Script Path")
    source_input = st.text_input(
        "Repo URL or local path",
        placeholder="https://github.com/org/repo.git or /path/to/project or /path/to/script.py",
    )
    run_triggered = st.button("🚀 Generate Workflow from Path / Repo", type="primary")

if run_triggered:
    working_dir = Path(tempfile.mkdtemp(prefix="code2flow_input_"))
    source_to_analyze: str | None = None

    if input_mode == "📝 Script Taker (Paste Code)":
        if not script_text.strip():
            st.warning("Please paste or write a script in the Script Taker text area.")
        else:
            lang_ext = target_language or "py"
            script_path = working_dir / f"script.{lang_ext}"
            script_path.write_text(script_text, encoding="utf-8")
            source_to_analyze = str(script_path)

    elif input_mode == "📂 Upload Script File":
        if uploaded_file is None or not script_text.strip():
            st.warning("Please upload a valid script file first.")
        else:
            filename = uploaded_file.name
            script_path = working_dir / filename
            script_path.write_bytes(uploaded_file.getvalue())
            source_to_analyze = str(script_path)

    else:
        cleaned_source = source_input.strip() if "source_input" in locals() else ""
        if not cleaned_source:
            st.warning("Please enter a repo URL or local path before generating the workflow.")
        elif cleaned_source.startswith(("http://", "https://")):
            with st.spinner("Cloning remote repository..."):
                try:
                    repo_dir = working_dir / "repo"
                    source_to_analyze = str(clone_repo(cleaned_source, repo_dir))
                except subprocess.CalledProcessError as err:
                    st.error(f"Failed to clone repository: {err}")
        else:
            local_p = Path(cleaned_source)
            if not local_p.exists():
                st.error(f"Local path does not exist: {cleaned_source}")
            else:
                source_to_analyze = str(local_p)

    if source_to_analyze:
        with st.spinner("Generating workflow diagram..."):
            try:
                dot_file, png_file, svg_file = generate_flowchart(
                    source_paths=source_to_analyze,
                    hide_legend=hide_legend,
                    no_grouping=no_grouping,
                    no_trimming=no_trimming,
                    language=target_language,
                )

                st.success("🎉 Workflow diagram generated successfully!")

                # Display image
                if png_file.exists():
                    st.image(str(png_file), caption="Generated Workflow Graph", use_container_width=True)

                # Download Buttons
                c1, c2, c3 = st.columns(3)
                if png_file.exists():
                    with open(png_file, "rb") as f:
                        c1.download_button(
                            label="📥 Download PNG Image",
                            data=f.read(),
                            file_name="workflow.png",
                            mime="image/png",
                            use_container_width=True,
                        )

                if svg_file and svg_file.exists():
                    with open(svg_file, "rb") as f:
                        c2.download_button(
                            label="📥 Download SVG Diagram",
                            data=f.read(),
                            file_name="workflow.svg",
                            mime="image/svg+xml",
                            use_container_width=True,
                        )

                if dot_file.exists():
                    with open(dot_file, "r", encoding="utf-8") as f:
                        dot_content = f.read()
                        c3.download_button(
                            label="📄 Download Graphviz DOT",
                            data=dot_content,
                            file_name="workflow.gv",
                            mime="text/vnd.graphviz",
                            use_container_width=True,
                        )

                # Expandable details
                if dot_file.exists():
                    with st.expander("🔍 View Graphviz DOT Code"):
                        st.code(dot_file.read_text(encoding="utf-8"), language="dot")

                if script_text.strip():
                    with st.expander("📝 View Analyzed Script"):
                        st.code(script_text, language=target_language or "python")

            except subprocess.CalledProcessError as exc:
                st.error(
                    f"Command failed while generating the flowchart. Check that Graphviz (`dot`) is installed.\n{exc}"
                )
            except Exception as exc:
                st.error(f"Unable to generate workflow. Details: {exc}")

st.markdown("---")
st.markdown(
    "Workflow visualizer built with `code2flow` and Graphviz. Supports scripts, multi-file projects, and remote repositories."
)
