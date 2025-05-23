import os
import pandas as pd
import streamlit as st
import json
from typing import Dict, List
import streamlit_permalink as stp


is_local = os.getenv("LOCAL", "True") == "True"

def update_query_dataframe(
    key: str, df: pd.DataFrame, append: bool, is_static: bool
) -> None:
    original_df = getattr(
        st.session_state,
        f"STREAMLIT_PERMALINK_DATA_EDITOR_{key}",
    )

    if append:
        new_df = pd.concat([original_df, df], ignore_index=True)

        if is_static:
            new_df = new_df.drop_duplicates(
                subset=["Residue"], keep="last"
            ).reset_index(drop=True)
        else:
            new_df = new_df.drop_duplicates(
                subset=["Residue", "Mass"], keep="last"
            ).reset_index(drop=True)

        st.query_params.update({key: stp.to_url_value(new_df)})
    else:
        st.query_params.update({key: stp.to_url_value(df)})

    st.rerun()


def main():

    # reset query params btn
    c1, c2, c3 = st.columns(3)

    # Open Search: set wide window = false, precursor tol to da, and -100 - 500
    # WWA/PRM/DIA: wide_window = true, chimeric=false, report_psms=5

    if c1.button(
        label="Apply Open Search Settings",
        type="secondary",
        key="open_search",
        use_container_width=True,
        help="Open Search settings(wide_window = false, precursor_tol=da, precursor_tol_minus=-100, precursor_tol_plus=500)",
    ):
        st.query_params.update({"wide_window": False})
        st.query_params.update({"precursor_tol_type": "da"})
        st.query_params.update({"precursor_tol_minus": -100})
        st.query_params.update({"precursor_tol_plus": 500})
        st.rerun()

    # WWA/PRM/DIA: set wide window = true, chimeric=false, report_psms=5
    if c2.button(
        label="Apply WWA/PRM/DIA Settings",
        type="secondary",
        key="wwa_prm_dia",
        use_container_width=True,
        help="WWA/PRM/DIA settings(wide_window = true, chimeric=false, report_psms=5)",
    ):
        st.query_params.update({"wide_window": True})
        st.query_params.update({"chimera": False})
        st.query_params.update({"report_psms": 5})
        st.rerun()


    if c3.button(
        label="Load Default",
        type="secondary",
        key="reset_query_params",
        use_container_width=True,
        help="Reset all query params to default values",
    ):
        st.query_params.clear()
        st.rerun()

    st.title("Sage Configuration Generator")

    with st.container(height=550):
        (
            file_tab,
            enzyme_tab,
            fragment_tab,
            static_mods_tab,
            variable_mods_tab,
            search_tolerance_tab,
            spectra_processing_tab,
            quantification_tab,
        ) = st.tabs(
            [
                "Input",
                "Enzyme",
                "Fragment",
                "Static Mods",
                "Variable Mods",
                "Search",
                "Spectra",
                "Quant",
            ]
        )

    error_container = st.empty()

    with file_tab:

        output_directory = st.text_input(
            label="Output Directory",
            value="output",
            help="Directory to save the output files.",
        )

        mzml_df = pd.DataFrame(columns=["mzML Path"])
        mzml_df["mzML Path"] = ["/path/to/mzml"]


        if is_local:
            c1, c2 = st.columns([2,1], vertical_alignment="center")

            with c1:
                folder_path = st.text_input(
                    label="Folder Path",
                    placeholder="path/to/folder",
                    value=None,
                    help="Path to the folder containing mzML files",
                )

                # fix folder path for windows
                if os.name == "nt" and folder_path:
                    folder_path = folder_path.replace("\\", "/")
                
            with c2:
                if st.button("Load Files", use_container_width=True):
                    # Load mzML files from the folder
                    if folder_path:
                        mzml_files = [
                            os.path.join(folder_path, f)
                            for f in os.listdir(folder_path)
                            if f.endswith(".mzML") or f.endswith(".mzml") or f.endswith(".mzML.gz") or f.endswith(".d")
                        ]
                        if len(mzml_files) == 0:
                            error_container.error(
                                "No mzML files found in the specified folder."
                            )
                        else:
                            mzml_df = pd.DataFrame(columns=["mzML Path"])
                            mzml_df["mzML Path"] = mzml_files
                            st.session_state.mzml_df = mzml_df
                    else:
                        error_container.error("Please specify a folder path.")
           

        st.caption("mzml paths")
        mzml_df = st.data_editor(
            mzml_df,
            column_config={
                "mzML Path": st.column_config.TextColumn(
                    label="mzML Path", help="Path to the mzML file"
                ),
            },
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True,
            height=245 if is_local else 300,
        )

        mzml_paths = mzml_df["mzML Path"].tolist()

    with enzyme_tab:

        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("Trypsin (KR!P)", use_container_width=True):
                # update query params cleave_at="KR"
                st.query_params.update({"cleave_at": "KR"})
                st.query_params.update({"restrict": "P"})
                st.query_params.update({"enzyme_terminus": "C"})
                st.query_params.update({"missed_cleavages": 2})
                st.rerun()

            # chymotrypsin
            if st.button("Chymotrypsin (FWYL!P)", use_container_width=True):
                # update query params cleave_at="FYW"
                st.query_params.update({"cleave_at": "FWYL"})
                st.query_params.update({"restrict": "P"})
                st.query_params.update({"enzyme_terminus": "C"})
                st.query_params.update({"missed_cleavages": 5})
                st.rerun()

            if st.button("Lys-C (K!P)", use_container_width=True):
                # update query params cleave_at="K"
                st.query_params.update({"cleave_at": "K"})
                st.query_params.update({"restrict": "P"})
                st.query_params.update({"enzyme_terminus": "C"})
                st.query_params.update({"missed_cleavages": 1})
                st.rerun()

            if st.button("Asp-N (DE)", use_container_width=True):
                # update query params cleave_at="DE"
                st.query_params.update({"cleave_at": "DE"})
                st.query_params.update({"restrict": ""})
                st.query_params.update({"enzyme_terminus": "N"})
                st.query_params.update({"missed_cleavages": 2})
                st.rerun()

            # protinase K
            if st.button("Protinase K (AEFILTVWY)", use_container_width=True):
                # update query params cleave_at="A"
                st.query_params.update({"cleave_at": "AEFILTVWY"})
                st.query_params.update({"restrict": ""})
                st.query_params.update({"enzyme_terminus": "C"})
                st.query_params.update({"missed_cleavages": 7})
                st.rerun()

            if st.button("Arg-C (R!P)", use_container_width=True):
                # update query params cleave_at="R"
                st.query_params.update({"cleave_at": "R"})
                st.query_params.update({"restrict": "P"})
                st.query_params.update({"enzyme_terminus": "C"})
                st.query_params.update({"missed_cleavages": 1})
                st.rerun()

            if st.button("Non-enzymatic ()", use_container_width=True):
                # update query params cleave_at="K"
                st.query_params.update({"cleave_at": ""})
                st.query_params.update({"restrict": ""})
                st.query_params.update({"enzyme_terminus": "C"})
                st.query_params.update({"missed_cleavages": 0})
                st.rerun()

            if st.button("No Digestion ($)", use_container_width=True):
                # update query params cleave_at="DE"
                st.query_params.update({"cleave_at": "$"})
                st.query_params.update({"restrict": ""})
                st.query_params.update({"enzyme_terminus": "C"})
                st.query_params.update({"missed_cleavages": 0})
                st.rerun()

        with c2:

            missed_cleavages = stp.number_input(
                label="Missed Cleavages",
                min_value=0,
                max_value=None,
                value=2,
                key="missed_cleavages",
                help="Number of missed cleavages.",
            )

            sc1, sc2 = st.columns(2)
            with sc1:
                min_len = stp.number_input(
                    "Minimum Peptide Length",
                    min_value=1,
                    max_value=None,
                    value=5,
                    key="min_len",
                    help="The minimum amino acid (AA) length of peptides to search",
                )

            with sc2:
                max_len = stp.number_input(
                    "Maximum Peptide Length",
                    min_value=1,
                    max_value=None,
                    value=50,
                    key="max_len",
                    help="The maximum amino acid (AA) length of peptides to search",
                )

            # assert min_len < max_len
            if min_len > max_len:
                error_container.error(
                    "Minimum length must be less than or equal to maximum length."
                )

            cleave_at = stp.text_input(
                label="Cleave At",
                value="KR",
                key="cleave_at",
                help="Amino acids to cleave at.",
            )
            restrict = stp.text_input(
                label="Restrict",
                value="P",
                key="restrict",
                help="Single character string. Do not cleave if this amino acid follows the cleavage site.",
            )

            sc1, sc2 = st.columns(2)
            with sc1:
                enzyme_terminus = stp.radio(
                    "Enzyme Terminus",
                    ["N", "C"],
                    index=1,
                    horizontal=True,
                    key="enzyme_terminus",
                    help="Select the enzyme terminus to use for the search.",
                )

            with sc2:
                semi_enzymatic = stp.checkbox(
                    "Semi-enzymatic",
                    value=False,
                    key="semi_enzymatic",
                    help="Select if the search should be semi-enzymatic.",
                )

    with fragment_tab:

        c1, c2 = st.columns([1, 2])

        with c1:

            st.caption("Resolution")

            if st.button("High Res MS/MS", use_container_width=True):
                # update query params bucket_size=8192
                st.query_params.update({"bucket_size": 8192})
                st.rerun()

            if st.button("Low Res MS/MS", use_container_width=True):
                # update query params bucket_size=32768
                st.query_params.update({"bucket_size": 65536})
                st.rerun()

            st.caption("Fragmentation")

            if st.button("CID/HCD", use_container_width=True):
                # update query params bucket_size=8192
                st.query_params.update({"fragment_ions": list("by")})
                st.rerun()
            if st.button("ETD/ECD", use_container_width=True):
                st.query_params.update({"fragment_ions": list("cz")})
                st.rerun()
            if st.button("UVPD", use_container_width=True):
                st.query_params.update({"fragment_ions": list("abcxyz")})
                st.rerun()
            if st.button("IRMPD", use_container_width=True):
                st.query_params.update({"fragment_ions": list("by")})
                st.rerun()

        with c2:
            sc1, sc2 = st.columns(2)
            with sc1:
                bucket_size = stp.selectbox(
                    label="Bucket Size",
                    options=[8192, 16384, 32768, 65536],
                    index=2,
                    accept_new_options=True,
                    help="Use lower values (8192) for high-res MS/MS, higher values for low-res MS/MS (only affects search speed)",
                    key="bucket_size",
                )
            with sc2:
                min_ion_index = stp.number_input(
                    label="Minimum Ion Index",
                    min_value=0,
                    max_value=None,
                    value=2,
                    key="min_ion_index",
                    help="Do not generate b1..bN or y1..yN ions for preliminary searching if min_ion_index = N. Does not affect full scoring of PSMs.",
                )

            ion_kinds = stp.segmented_control(
                label="Fragment Ions",
                options=list("abcxyz"),
                default=list("by"),
                key="fragment_ions",
                help="Select the fragment ions to use for the search.",
                selection_mode="multi",
            )

            if len(ion_kinds) == 0:
                error_container.error("At least one ion type must be selected.")

            max_fragment_charge = stp.number_input(
                label="Maximum Fragment Charge",
                min_value=1,
                max_value=None,
                value=None,
                key="max_fragment_charge",
                help="Maximum charge state of fragment ions to use for the search.",
            )

            peptide_min_mass = stp.number_input(
                "Peptide Minimum Mass",
                min_value=0.0,
                max_value=None,
                value=500.0,
                key="peptide_min_mass",
                help="Minimum mass of peptides to search.",
            )
            peptide_max_mass = stp.number_input(
                "Peptide Maximum Mass",
                min_value=0.0,
                max_value=None,
                value=5000.0,
                key="peptide_max_mass",
                help="Maximum mass of peptides to search.",
            )

            if peptide_min_mass >= peptide_max_mass:
                error_container.error("Minimum mass must be less than maximum mass.")

    with static_mods_tab:

        c1, c2 = st.columns([1, 2])

        with c1:
            if st.button("Carbamidomethylation (C)", use_container_width=True):
                cysteine_df = pd.DataFrame({"Residue": ["C"], "Mass": [57.0215]})
                update_query_dataframe("static_mods", cysteine_df, True, True)
            if st.button("TMT 2-plex (K^)", use_container_width=True):
                tmt_2plex_df = pd.DataFrame(
                    {"Residue": ["K", "^"], "Mass": [225.1558, 225.1558]}
                )
                update_query_dataframe("static_mods", tmt_2plex_df, True, True)
            if st.button("TMT 6-plex (K^)", use_container_width=True):
                tmt_6plex_df = pd.DataFrame(
                    {"Residue": ["K", "^"], "Mass": [229.1629, 229.1629]}
                )
                update_query_dataframe("static_mods", tmt_6plex_df, True, True)
            if st.button("TMT 10-plex (K^)", use_container_width=True):
                tmt_10plex_df = pd.DataFrame(
                    {"Residue": ["K", "^"], "Mass": [229.1629, 304.2071]}
                )
                update_query_dataframe("static_mods", tmt_10plex_df, True, True)
            if st.button("TMT 16-plex (K^)", use_container_width=True):
                tmt_16plex_df = pd.DataFrame(
                    {"Residue": ["K", "^"], "Mass": [304.2071, 304.2071]}
                )
                update_query_dataframe("static_mods", tmt_16plex_df, True, True)
            if st.button("iTRAQ (K^)", use_container_width=True):
                itraq_df = pd.DataFrame(
                    {"Residue": ["K", "^"], "Mass": [144.1021, 144.1021]}
                )
                update_query_dataframe("static_mods", itraq_df, True, True)
            if st.button("Dimethyl (K^)", use_container_width=True):
                dimethyl_df = pd.DataFrame(
                    {"Residue": ["K", "^"], "Mass": [28.0313, 28.0313]}
                )
                update_query_dataframe("static_mods", dimethyl_df, True, True)
            if st.button(
                "Clear",
                use_container_width=True,
                type="primary",
                key="clear_static_mods",
            ):
                empty_df = pd.DataFrame(columns=["Residue", "Mass"])
                update_query_dataframe("static_mods", empty_df, False, True)

        with c2:
            static_mods = stp.data_editor(
                pd.DataFrame({"Residue": ["C"], "Mass": [57.0215]}),
                column_config={
                    "Residue": st.column_config.TextColumn("Residue", help="Residue"),
                    "Mass": st.column_config.NumberColumn(
                        "Mass", format="%.5f", help="Mass of modification"
                    ),
                },
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                key="static_mods",
                height=420,
            )

        # check that no duplicate residues are selected
        if len(static_mods) != 0 and static_mods["Residue"].duplicated().any():
            error_container.error(
                "Duplicate residues selected in static modifications."
            )

        static_dict: Dict[str, float] = {}
        for index, row in static_mods.iterrows():
            residue = row["Residue"]
            mass = row["Mass"]
            static_dict[residue] = mass

    with variable_mods_tab:
        var_df = pd.DataFrame({"Residue": ["M"], "Mass": [15.9949]})

        c1, c2 = st.columns([1, 2])

        with c1:
            if st.button("Phosphorylation (STY)", use_container_width=True):
                phospho_df = pd.DataFrame(
                    {"Residue": ["S", "T", "Y"], "Mass": [79.9663, 79.9663, 79.9663]}
                )
                update_query_dataframe("variable_mods", phospho_df, True, False)
            if st.button("Acetylation (K)", use_container_width=True):
                acetyl_df = pd.DataFrame({"Residue": ["K"], "Mass": [42.0106]})
                update_query_dataframe("variable_mods", acetyl_df, True, False)
            if st.button("Methylation (KR)", use_container_width=True):
                methyl_df = pd.DataFrame(
                    {"Residue": ["K", "R"], "Mass": [14.0157, 14.0157]}
                )
                update_query_dataframe("variable_mods", methyl_df, True, False)
            if st.button("Oxidation (M)", use_container_width=True):
                oxidation_df = pd.DataFrame({"Residue": ["M"], "Mass": [15.9949]})
                update_query_dataframe("variable_mods", oxidation_df, True, False)
            if st.button("Deamidation (NQ)", use_container_width=True):
                deamidation_df = pd.DataFrame(
                    {"Residue": ["N", "Q"], "Mass": [0.9840, 0.9840]}
                )
                update_query_dataframe("variable_mods", deamidation_df, True, False)
            if st.button("Ubiquitination (K)", use_container_width=True):
                ubiquitination_df = pd.DataFrame({"Residue": ["K"], "Mass": [114.0429]})
                update_query_dataframe("variable_mods", ubiquitination_df, True, False)
            if st.button("Methyl Ester (DE)", use_container_width=True):
                methyl_ester_df = pd.DataFrame(
                    {"Residue": ["D", "E"], "Mass": [14.0157, 14.0157]}
                )
                update_query_dataframe("variable_mods", methyl_ester_df, True, False)
            if st.button(
                "Clear",
                use_container_width=True,
                type="primary",
                key="clear_variable_mods",
            ):
                empty_df = pd.DataFrame(columns=["Residue", "Mass"])
                update_query_dataframe("variable_mods", empty_df, False, False)

        with c2:
            max_variable_mods = stp.number_input(
                label="Max Variable Modifications",
                min_value=1,
                max_value=None,
                value=3,
                key="max_variable_mods",
                help="Maximum number of variable modifications to use for the search.",
            )

            variable_mods = stp.data_editor(
                var_df,
                column_config={
                    "Residue": st.column_config.TextColumn("Residue", help="Residue"),
                    "Mass": st.column_config.NumberColumn(
                        "Mass", format="%.5f", help="Mass of modification"
                    ),
                },
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                key="variable_mods",
                height=350,
            )

        # check no duplicated residue and mass pairs
        if (
            len(variable_mods) != 0
            and variable_mods.duplicated(subset=["Residue", "Mass"]).any()
        ):
            error_container.error(
                "Duplicate residue and mass pairs selected in variable modifications."
            )

        variable_dict: Dict[str, List[float]] = {}
        for index, row in variable_mods.iterrows():
            residue = row["Residue"]
            mass = row["Mass"]

            if residue in variable_dict:
                variable_dict[residue].append(mass)
            else:
                variable_dict[residue] = [mass]

    with search_tolerance_tab:

        wide_window = stp.checkbox(
            label="Wide Window",
            value=False,
            key="wide_window",
            help="This parameter instructs Sage to dynamically change the precursor tolerance for each spectra based on the isolation window encoded in the mzML file",
        )

        c1, c2 = st.columns(2)
        with c1:
            precursor_tol_minus = stp.number_input(
                label="Precursor Tolerance Minus",
                value=-50,
                max_value=0,
                key="precursor_tol_minus",
                help="Precursor tolerance in Da or ppm",
                disabled=wide_window,
            )
            precursor_tol_plus = stp.number_input(
                label="Precursor Tolerance Plus",
                value=50,
                min_value=0,
                key="precursor_tol_plus",
                help="Precursor tolerance in Da or ppm",
                disabled=wide_window,
            )
            precursor_tol_type = stp.selectbox(
                label="Precursor Tolerance Type",
                options=["ppm", "da"],
                index=0,
                help="Type of fragment tolerance to use",
                key="precursor_tol_type",
                disabled=wide_window,
            )
        with c2:
            fragment_tol_minus = stp.number_input(
                label="Fragment Tolerance Minus",
                value=-50,
                max_value=0,
                key="fragment_tol_minus",
                help="Fragment tolerance in Da or ppm",
            )
            fragment_tol_plus = stp.number_input(
                label="Fragment Tolerance Plus",
                value=50,
                min_value=0,
                key="fragment_tol_plus",
                help="Fragment tolerance in Da or ppm",
            )
            fragment_tol_type = stp.selectbox(
                label="Fragment Tolerance Units",
                options=["ppm", "da"],
                index=0,
                help="Units for fragment tolerance",
                key="fragment_tol_type",
            )

        fasta_path = stp.text_input(
            label="FASTA Path",
            placeholder="path/to/fasta",
            value=None,
            key="fasta_path",
            help="Path to the FASTA file",
        )
        c1, c2 = st.columns(2, vertical_alignment="center")
        with c1:
            decoy_tag = stp.text_input(
                label="Decoy Tag",
                value="rev_",
                key="decoy_tag",
                help="The tag used to identify decoy entries in the FASTA database",
            )
        with c2:
            generate_decoys = stp.checkbox(
                label="Generate Decoys",
                value=False,
                key="generate_decoys",
                help="If true, ignore decoys in the FASTA database matching decoy_tag, and generate internally reversed peptides",
            )

    with spectra_processing_tab:

        c1, c2, c3 = st.columns(3)
        with c1:
            deisotope = stp.checkbox(
                label="Deisotope",
                value=False,
                key="deisotope",
                help="Deisotope the MS2 spectra",
            )
        with c2:
            chimera = stp.checkbox(
                label="Chimera",
                value=False,
                key="chimera",
                help="Search for chimeric/co-fragmenting PSMs",
            )

        with c3:
            predict_rt = stp.checkbox(
                label="Predict RT",
                value=True,
                key="predict_rt",
                help="Predict retention time for the peptides. (You probably don't want to turn this off without good reason!)",
            )

        c1, c2 = st.columns(2)
        with c1:
            precursor_charge_min = stp.number_input(
                label="Minimum Precursor Charge",
                min_value=1,
                max_value=None,
                value=2,
                key="precursor_charge_min",
                help="Minimum charge state of precursor ions to use for the search",
            )
        with c2:
            precursor_charge_max = stp.number_input(
                label="Maximum Precursor Charge",
                min_value=1,
                max_value=None,
                value=4,
                key="precursor_charge_max",
                help="Maximum charge state of precursor ions to use for the search",
            )

        if precursor_charge_min > precursor_charge_max:
            error_container.error(
                "Minimum charge must be less than  or equal to maximum charge."
            )

        c1, c2 = st.columns(2)
        with c1:
            isotope_error_min = stp.number_input(
                label="Minimum Isotope Error",
                min_value=None,
                max_value=0,
                value=-1,
                key="isotope_error_min",
                help="Minimum number of isotopes to use for the search",
            )
        with c2:
            isotope_error_max = stp.number_input(
                label="Maximum Isotope Error",
                min_value=0,
                max_value=None,
                value=3,
                key="isotope_error_max",
                help="Maximum number of isotopes to use for the search",
            )

        c1, c2 = st.columns(2)
        with c1:
            min_peaks = stp.number_input(
                label="Minimum Peaks",
                min_value=0,
                max_value=None,
                value=15,
                key="min_spectra_peaks",
                help="Only process MS2 spectra with at least N peaks",
            )
        with c2:
            max_peaks = stp.number_input(
                label="Maximum Peaks",
                min_value=0,
                max_value=None,
                value=150,
                key="max_spectra_peaks",
                help="Take the top N most intense MS2 peaks to search",
            )

        if min_peaks > max_peaks:
            error_container.error(
                "Minimum peaks must be less than or equal to maximum peaks."
            )

        c1, c2 = st.columns(2)
        with c1:
            min_matched_peaks = stp.number_input(
                label="Minimum Matched Peaks",
                min_value=1,
                max_value=None,
                value=6,
                key="min_matched_peaks",
                help="Minimum number of matched peaks to report PSMs",
            )
        with c2:
            report_psms = stp.number_input(
                label="Report PSMs",
                min_value=1,
                max_value=None,
                value=1,
                key="report_psms",
                help="The number of PSMs to report for each spectrum. Higher values might disrupt re-scoring, it is best to search with multiple values",
            )

    with quantification_tab:
        quant_type = stp.radio(
            label="Quantification Type",
            options=["None", "TMT", "LFQ"],
            horizontal=True,
            index=0,
            key="quant_type",
            help="Select the quantification type to use for the search",
        )
        if quant_type == "TMT":

            c1, c2 = st.columns(2)
            with c1:
                tmt_type = stp.selectbox(
                    label="TMT Type",
                    options=["Tmt6", "Tmt10", "Tmt11", "Tmt16", "Tmt18"],
                    index=3,
                    key="tmt_type",
                    help="Select the TMT type to use for the search",
                )
            with c2:
                tmt_level = stp.number_input(
                    label="TMT Level",
                    value=3,
                    min_value=0,
                    key="tmt_level",
                    help="The MS-level to perform TMT quantification on",
                )
            tmt_sn = stp.checkbox(
                label="Use Signal/Noise instead of intensity",
                value=False,
                key="tmt_sn",
                help="Use Signal/Noise instead of intensity for TMT quantification. Requires noise values in mzML",
            )

        if quant_type == "LFQ":

            c1, c2 = st.columns(2)
            with c1:
                lfq_peak_scoring = stp.selectbox(
                    label="LFQ Peak Scoring",
                    options=["Hybrid", "Simple"],
                    index=0,
                    key="lfq_peak_scoring",
                    help="The method used for scoring peaks in LFQ",
                )
            lfq_integration = stp.selectbox(
                label="LFQ Integration",
                options=["Sum", "Apex"],
                index=0,
                key="lfq_integration",
                help="The method used for integrating peak intensities",
            )
            with c2:
                lfq_spectral_angle = stp.number_input(
                    label="LFQ Spectral Angle",
                    min_value=0.0,
                    max_value=None,
                    value=0.7,
                    key="lfq_spectral_angle",
                    help="Threshold for the normalized spectral angle similarity measure (observed vs theoretical isotopic envelope)",
                )

            c1, c2 = st.columns(2)
            with c1:
                lfq_ppm_tolerance = stp.number_input(
                    label="LFQ PPM Tolerance",
                    min_value=0.0,
                    max_value=None,
                    value=5.0,
                    key="lfq_ppm_tolerance",
                    help="Tolerance for matching MS1 ions in parts per million",
                )
            with c2:
                lfq_mobility_pct_tolerance = stp.number_input(
                    label="LFQ Mobility % Tolerance",
                    min_value=0.0,
                    max_value=None,
                    value=3.0,
                    key="lfq_mobility_pct_tolerance",
                    help="Tolerance for matching MS1 ions in percent (default: 3.0). Only used for Bruker input.",
                )

            combine_charge_states = stp.checkbox(
                label="Combine Charge States",
                value=True,
                key="combine_charge_states",
                help="Combine charge states for LFQ quantification",
            )

    # Build config dictionary
    config = {}

    # Database section
    config["database"] = {
        "bucket_size": bucket_size,
        "enzyme": {
            "missed_cleavages": missed_cleavages,
            "min_len": min_len,
            "max_len": max_len,
            "cleave_at": cleave_at,
            "restrict": restrict,
            "c_terminal": enzyme_terminus == "C",
            "semi_enzymatic": semi_enzymatic,
        },
        "peptide_min_mass": peptide_min_mass,
        "peptide_max_mass": peptide_max_mass,
        "ion_kinds": ion_kinds,
        "min_ion_index": min_ion_index,
        "decoy_tag": decoy_tag,
        "generate_decoys": generate_decoys,
        "fasta": fasta_path,
    }

    if static_dict:
        config["database"]["static_mods"] = static_dict

    if variable_dict:
        config["database"]["variable_mods"] = variable_dict
        config["database"]["max_variable_mods"] = max_variable_mods

    # Add quantification section if selected
    if quant_type != "None":
        config["quant"] = {}

        if quant_type == "TMT":
            config["quant"]["tmt"] = tmt_type
            config["quant"]["tmt_settings"] = {"level": tmt_level, "sn": tmt_sn}

        if quant_type == "LFQ":
            config["quant"]["lfq"] = True
            config["quant"]["lfq_settings"] = {
                "peak_scoring": lfq_peak_scoring,
                "integration": lfq_integration,
                "spectral_angle": lfq_spectral_angle,
                "ppm_tolerance": lfq_ppm_tolerance,
                "mobility_pct_tolerance": lfq_mobility_pct_tolerance,
                "combine_charge_states": combine_charge_states,
            }

    # Tolerance section
    config["precursor_tol"] = {
        precursor_tol_type: [precursor_tol_minus, precursor_tol_plus]
    }

    config["fragment_tol"] = {
        fragment_tol_type: [fragment_tol_minus, fragment_tol_plus]
    }

    # Additional settings
    config["precursor_charge"] = [precursor_charge_min, precursor_charge_max]
    config["isotope_errors"] = [isotope_error_min, isotope_error_max]
    config["deisotope"] = deisotope
    config["chimera"] = chimera
    config["wide_window"] = wide_window
    config["predict_rt"] = predict_rt
    config["min_peaks"] = min_peaks
    config["max_peaks"] = max_peaks
    config["min_matched_peaks"] = min_matched_peaks
    config["max_fragment_charge"] = max_fragment_charge
    config["report_psms"] = report_psms
    config["output_directory"] = output_directory

    # mzML paths
    config["mzml_paths"] = mzml_paths

    # Generate JSON
    config_json = json.dumps(config, indent=2)

    # Display preview of the JSON
    st.subheader("Generated Configuration")
    st.code(config_json, language="json", height=500)

    file_name = st.text_input("File Name", value="sage_config.json")
    st.download_button(
        label="Download JSON",
        data=config_json,
        file_name=file_name,
        mime="application/json",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
