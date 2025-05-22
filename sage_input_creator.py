import pandas as pd
import streamlit as st
import json
import base64
from typing import Dict, List, Any, Optional, Union
import streamlit_permalink as stp


# reset query params btn
if st.button("Reset Query Params"):
    st.query_params.clear()
    st.rerun()

example_links = {
    'Open Search': f'{st.context.url}?FASTA+Path=dual.fasta&Decoy+Tag=rev_&Generate+Decoys=False&Missed+Cleavages=2&Minimum+Peptide+Length=5&Maximum+Peptide+Length=50&Cleave+At=KR&Restrict=P&Enzyme+Terminus=N&Bucket+Size+%28fragments+in+each+mass+bucket%29=32768&Minimum+Ion+Index=2&Ion+Kinds=b&Ion+Kinds=y&Peptide+Minimum+Mass=500.0&Peptide+Maximum+Mass=5000.0&missed_cleavages=2&min_len=8&max_len=50&cleave_at=KR&restrict=P&enzyme_terminus=N&bucket_size=32768&min_ion_index=2&ion_kinds=b&ion_kinds=y&peptide_min_mass=500.0&peptide_max_mass=5000.0&static_mods=%5B%7B"Residue"%3A"C"%2C"Mass"%3A57.0215%7D%5D&Max+Variable+Modifications=3&variable_mods=%5B%7B"Residue"%3A"M"%2C"Mass"%3A15.9949%7D%5D&precursor_tol_minus=-500&precursor_tol_plus=100&precursor_tol_type=da&fragment_tol_minus=-10&fragment_tol_plus=10&fragment_tol_type=ppm&Minimum+Precursor+Charge=2&Maximum+Precursor+Charge=4&isotope_error_min=-1&isotope_error_max=3&min_spectra_peaks=15&max_spectra_peaks=150&min_matched_peaks=6&max_fragment_charge=1&report_psms=1&deisotope=False&chimera=False&wide_window=False&predict_rt=False&quant_type=None',
}

def update_query_dataframe(key: str, df: pd.DataFrame, append: bool, is_static: bool) -> None:
    original_df = getattr(
                            st.session_state,
                            f'STREAMLIT_PERMALINK_DATA_EDITOR_{key}',
                        )
    
    if append:
        new_df = pd.concat([original_df, df], ignore_index=True)

        if is_static:
            new_df = new_df.drop_duplicates(subset=["Residue"], keep="last").reset_index(drop=True)
        else:
            new_df = new_df.drop_duplicates(subset=["Residue", "Mass"], keep="last").reset_index(drop=True)

        st.query_params.update({key: stp.to_url_value(new_df)})
    else:
        st.query_params.update({key: stp.to_url_value(df)})

    st.rerun()

def main():
    st.title("Sage Configuration Generator")
    st.write("Generate a configuration file for Sage proteomics search engine")

    # load example links
    st.subheader("Example Links")
    st.write("Click on the links below to load example configurations.")
    for name, link in example_links.items():
        st.markdown(f"[{name}]({link})")
    
    with st.container(height=520):
        file_tab, enzyme_tab, fragment_tab, static_mods_tab, variable_mods_tab, search_tolerance_tab, spectra_processing_tab, quantification_tab = st.tabs(
            ["Input", "Enzyme", "Fragment", "Static Mods", "Variable Mods", "Search", "Spectra", "Quant"]
        )

    error_container = st.empty()

    with file_tab:

        output_directory = st.text_input("Output Directory", value="./output")
    
        mzml_df = pd.DataFrame(columns=["mzML Path"])
        mzml_df["mzML Path"] = ["local/path.mzML"]

        st.caption("mzml paths")
        mzml_df = st.data_editor(
            mzml_df,
            column_config={
                "mzML Path": st.column_config.TextColumn("mzML Path")
            },
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True,
            height=300,
        )

        mzml_paths = mzml_df["mzML Path"].tolist()




    with enzyme_tab:

        missed_cleavages = stp.number_input("Missed Cleavages", min_value=0, max_value=None, value=2, key="missed_cleavages")

        c1, c2 = st.columns(2)
        with c1:
            min_len = stp.number_input("Minimum Peptide Length", min_value=1, max_value=None, value=5, key="min_len")

        with c2:
            max_len = stp.number_input("Maximum Peptide Length", min_value=1, max_value=None, value=50, key="max_len")

        # assert min_len < max_len
        if min_len > max_len:
            error_container.error("Minimum length must be less than or equal to maximum length.")


        cleave_at = stp.text_input("Cleave At", value="KR", key="cleave_at")

        restrict = stp.text_input("Restrict", value="P", key="restrict")
        
        enzyme_terminus = stp.radio("Enzyme Terminus", ["N", "C"], index=0, horizontal=True, key="enzyme_terminus")


    with fragment_tab:

        c1, c2 = st.columns(2)
        with c1:
            bucket_size = stp.selectbox(
                "Bucket Size (fragments in each mass bucket)", 
                [8192, 16384, 32768, 65536], 
                index=2,
                accept_new_options=True,
                help="Use lower values (8192) for high-res MS/MS, higher values for low-res MS/MS",
                key="bucket_size"
            )
        with c2:
            min_ion_index = stp.number_input("Minimum Ion Index", min_value=0, max_value=10, value=2, key="min_ion_index")

        ion_kinds = stp.segmented_control(
            "Fragment Ions",
            options=["a", "b", "c", "x", "y", "z"],
            default=["b", "y"],
            key="fragment_ions",
            help="Select the fragment ions to include in the search. Default is b and y ions.",
            selection_mode="multi",
        )

        if len(ion_kinds) == 0:
            error_container.error("At least one ion type must be selected.")

        max_fragment_charge = stp.number_input("Maximum Fragment Charge", min_value=1, max_value=None, value=1, key="max_fragment_charge")

        c1, c2 = st.columns(2)
        with c1:
            peptide_min_mass = stp.number_input("Peptide Minimum Mass", min_value=0.0, max_value=None, value=500.0, key="peptide_min_mass")
        
        with c2:
            peptide_max_mass = stp.number_input("Peptide Maximum Mass", min_value=0.0, max_value=None, value=5000.0, key="peptide_max_mass")
        
        if peptide_min_mass >= peptide_max_mass:
            error_container.error("Minimum mass must be less than maximum mass.")


    with static_mods_tab:

        c1, c2 = st.columns([1, 2])
        
        with c1:
            if st.button("Carbamidomethylation (C)", use_container_width=True):
                cysteine_df = pd.DataFrame({'Residue': ['C'], 'Mass': [57.0215]})
                update_query_dataframe("static_mods", cysteine_df, True, True)
            if st.button("TMT 2-plex (K^)", use_container_width=True):
                tmt_2plex_df = pd.DataFrame({'Residue': ['K', '^'], 'Mass': [225.1558, 225.1558]})
                update_query_dataframe("static_mods", tmt_2plex_df, True, True)
            if st.button("TMT 6-plex (K^)", use_container_width=True):
                tmt_6plex_df = pd.DataFrame({'Residue': ['K', '^'], 'Mass': [229.1629, 229.1629]})
                update_query_dataframe("static_mods", tmt_6plex_df, True, True)
            if st.button("TMT 10-plex (K^)", use_container_width=True):
                tmt_10plex_df = pd.DataFrame({'Residue': ['K', '^'], 'Mass': [229.1629, 304.2071]})
                update_query_dataframe("static_mods", tmt_10plex_df, True, True)
            if st.button("TMT 16-plex (K^)", use_container_width=True):
                tmt_16plex_df = pd.DataFrame({'Residue': ['K', '^'], 'Mass': [304.2071, 304.2071]})
                update_query_dataframe("static_mods", tmt_16plex_df, True, True)
            if st.button("iTRAQ (K^)", use_container_width=True):
                itraq_df = pd.DataFrame({'Residue': ['K', '^'], 'Mass': [144.1021, 144.1021]})
                update_query_dataframe("static_mods", itraq_df, True, True)
            if st.button("Dimethyl (K^)", use_container_width=True):
                dimethyl_df = pd.DataFrame({'Residue': ['K', '^'], 'Mass': [28.0313, 28.0313]})
                update_query_dataframe("static_mods", dimethyl_df, True, True)
            if st.button("Clear", use_container_width=True, type="primary", key="clear_static_mods"):
                empty_df = pd.DataFrame(columns=["Residue", "Mass"])
                update_query_dataframe("static_mods", empty_df, False, True)

        with c2:
            static_mods = stp.data_editor(
                pd.DataFrame({'Residue': ['C'], 'Mass': [57.0215]}),
                column_config={
                    "Residue": st.column_config.TextColumn("Residue"),
                    "Mass": st.column_config.NumberColumn("Mass", format="%.5f")
                },
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                key="static_mods",
                height=420
            )

        # check that no duplicate residues are selected
        if len(static_mods) != 0 and static_mods["Residue"].duplicated().any():
            error_container.error("Duplicate residues selected in static modifications.")

        static_dict: Dict[str, float] = {}
        for index, row in static_mods.iterrows():
            residue = row["Residue"]
            mass = row["Mass"]
            static_dict[residue] = mass
                


    with variable_mods_tab:
        var_df = pd.DataFrame({'Residue': ['M'], 'Mass': [15.9949]})

        c1, c2 = st.columns([1, 2])

        with c1:
            if st.button("Phosphorylation (STY)", use_container_width=True):
                phospho_df = pd.DataFrame({'Residue': ['S', 'T', 'Y'], 'Mass': [79.9663, 79.9663, 79.9663]})
                update_query_dataframe("variable_mods", phospho_df, True, False)
            if st.button("Acetylation (K)", use_container_width=True):
                acetyl_df = pd.DataFrame({'Residue': ['K'], 'Mass': [42.0106]})
                update_query_dataframe("variable_mods", acetyl_df, True, False)
            if st.button("Methylation (KR)", use_container_width=True):
                methyl_df = pd.DataFrame({'Residue': ['K', 'R'], 'Mass': [14.0157, 14.0157]})
                update_query_dataframe("variable_mods", methyl_df, True, False)
            if st.button("Oxidation (M)", use_container_width=True):
                oxidation_df = pd.DataFrame({'Residue': ['M'], 'Mass': [15.9949]})
                update_query_dataframe("variable_mods", oxidation_df, True, False)
            if st.button("Deamidation (NQ)", use_container_width=True):
                deamidation_df = pd.DataFrame({'Residue': ['N', 'Q'], 'Mass': [0.9840, 0.9840]})
                update_query_dataframe("variable_mods", deamidation_df, True, False)
            if st.button('Ubiquitination (K)', use_container_width=True):
                ubiquitination_df = pd.DataFrame({'Residue': ['K'], 'Mass': [114.0429]})
                update_query_dataframe("variable_mods", ubiquitination_df, True, False)
            if st.button("Methyl Ester (DE)", use_container_width=True):
                methyl_ester_df = pd.DataFrame({'Residue': ['D', 'E'], 'Mass': [14.0157, 14.0157]})
                update_query_dataframe("variable_mods", methyl_ester_df, True, False)
            if st.button("Clear", use_container_width=True, type="primary", key="clear_variable_mods"):
                empty_df = pd.DataFrame(columns=["Residue", "Mass"])
                update_query_dataframe("variable_mods", empty_df, False, False)

        with c2:
            max_variable_mods = stp.number_input("Max Variable Modifications", min_value=1, max_value=None, value=3)

            variable_mods = stp.data_editor(
                var_df,
                column_config={
                    "Residue": st.column_config.TextColumn("Residue"),
                    "Mass": st.column_config.NumberColumn("Mass", format="%.5f")
                },
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                key="variable_mods",
                height=350
            )

        # check no duplicated residue and mass pairs
        if len(variable_mods) != 0 and variable_mods.duplicated(subset=["Residue", "Mass"]).any():
            error_container.error("Duplicate residue and mass pairs selected in variable modifications.")

        variable_dict: Dict[str, List[float]] = {}
        for index, row in variable_mods.iterrows():
            residue = row["Residue"]
            mass = row["Mass"]

            if residue in variable_dict:
                variable_dict[residue].append(mass)
            else:
                variable_dict[residue] = [mass]

    with search_tolerance_tab:
        c1, c2 = st.columns(2)
        with c1:
            precursor_tol_minus = stp.number_input(f"Precursor Tolerance Minus", value=-50, max_value=0, key="precursor_tol_minus")
            precursor_tol_plus = stp.number_input(f"Precursor Tolerance Plus", value=50, min_value=0, key="precursor_tol_plus")
            precursor_tol_type = stp.selectbox("Precursor Tolerance Type", ["ppm", "da"], index=0, help="Type of fragment tolerance to use", key="precursor_tol_type")
        with c2:
            fragment_tol_minus = stp.number_input(f"Fragment Tolerance Minus", value=-50, max_value=0, key="fragment_tol_minus")
            fragment_tol_plus = stp.number_input(f"Fragment Tolerance Plus", value=50, min_value=0, key="fragment_tol_plus")
            fragment_tol_type = stp.selectbox("Fragment Tolerance Units", ["ppm", "da"], index=0, help="Units for fragment tolerance", key="fragment_tol_type")

        fasta_path = stp.text_input("FASTA Path", value="dual.fasta")
        c1, c2 = st.columns(2, vertical_alignment="center")
        with c1:
            decoy_tag = stp.text_input("Decoy Tag", value="rev_")
        with c2:
            generate_decoys = stp.checkbox("Generate Decoys", value=False)

    with spectra_processing_tab:
        c1, c2 = st.columns(2)
        with c1:
            precursor_charge_min = stp.number_input("Minimum Precursor Charge", min_value=1, max_value=None, value=2)
        with c2:
            precursor_charge_max = stp.number_input("Maximum Precursor Charge", min_value=1, max_value=None, value=4)

        if precursor_charge_min > precursor_charge_max:
            error_container.error("Minimum charge must be less than  or equal to maximum charge.")
        
        c1, c2 = st.columns(2)
        with c1:
            isotope_error_min = stp.number_input("Minimum Isotope Error", min_value=None, max_value=0, value=-1, key="isotope_error_min")
        with c2:
            isotope_error_max = stp.number_input("Maximum Isotope Error", min_value=0, max_value=None, value=3, key="isotope_error_max")

        
        c1, c2 = st.columns(2)
        with c1:
            min_peaks = stp.number_input("Minimum Peaks", min_value=0, max_value=None, value=15, key="min_spectra_peaks")
        with c2:
            max_peaks = stp.number_input("Maximum Peaks", min_value=0, max_value=None, value=150, key="max_spectra_peaks")

        if min_peaks > max_peaks:
            error_container.error("Minimum peaks must be less than or equal to maximum peaks.")


        c1, c2 = st.columns(2)
        with c1:
            min_matched_peaks = stp.number_input("Minimum Matched Peaks", min_value=1, max_value=None, value=6, key="min_matched_peaks")
        with c2:
            report_psms = stp.number_input("Report PSMs", min_value=1, max_value=None, value=1, key="report_psms")


        c1, c2, c3, c4 = st.columns(4)
        with c1:
            deisotope = stp.checkbox("Deisotope", value=False, key="deisotope")
        with c2:
            chimera = stp.checkbox("Chimera", value=False, key="chimera")
        with c3:
            wide_window = stp.checkbox("Wide Window", value=False, key="wide_window")
        with c4:
            predict_rt = stp.checkbox("Predict RT", value=False, key="predict_rt")

    with quantification_tab:
        quant_type = stp.radio("Quantification Type", ["None", "TMT", "LFQ"], horizontal=True, index=0, key="quant_type")
        if quant_type == "TMT":
            
            c1, c2 = st.columns(2)
            with c1:
                tmt_type = stp.selectbox("TMT Type", ["Tmt6", "Tmt10", "Tmt11", "Tmt16", "Tmt18"], index=3, key="tmt_type")
            with c2:
                tmt_level = stp.number_input("TMT Level", value=3, min_value=0, key="tmt_level")
            tmt_sn = stp.checkbox("Use Signal/Noise instead of intensity", value=False, key="tmt_sn")
        
        if quant_type == "LFQ":
                    
            c1, c2 = st.columns(2)
            with c1:
                lfq_peak_scoring = stp.selectbox("LFQ Peak Scoring", ["Hybrid", "Simple"], index=0, key="lfq_peak_scoring")
            lfq_integration = stp.selectbox("LFQ Integration", ["Sum", "Apex"], index=0, key="lfq_integration")
            with c2:
                lfq_spectral_angle = stp.number_input("LFQ Spectral Angle", min_value=0.0, max_value=None, value=0.7, key="lfq_spectral_angle")
            
            c1, c2 = st.columns(2)
            with c1:
                lfq_ppm_tolerance = stp.number_input("LFQ PPM Tolerance", min_value=0.0, max_value=None, value=5.0, key="lfq_ppm_tolerance")
            with c2:
                lfq_mobility_pct_tolerance = stp.number_input("LFQ Mobility % Tolerance", min_value=0.0, max_value=None, value=3.0, key="lfq_mobility_pct_tolerance")
        
    

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
        },
        "peptide_min_mass": peptide_min_mass,
        "peptide_max_mass": peptide_max_mass,
        "ion_kinds": ion_kinds,
        "min_ion_index": min_ion_index,
        "decoy_tag": decoy_tag,
        "generate_decoys": generate_decoys,
        "fasta": fasta_path
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
            config["quant"]["tmt_settings"] = {
                "level": tmt_level,
                "sn": tmt_sn
            }
        
        if quant_type == "LFQ":
            config["quant"]["lfq"] = True
            config["quant"]["lfq_settings"] = {
                "peak_scoring": lfq_peak_scoring,
                "integration": lfq_integration,
                "spectral_angle": lfq_spectral_angle,
                "ppm_tolerance": lfq_ppm_tolerance,
                "mobility_pct_tolerance": lfq_mobility_pct_tolerance
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
    st.code(config_json, language='json', height=500)
    
    file_name = st.text_input("File Name", value="sage_config.json")
    st.download_button(
        label="Download JSON",
        data=config_json,
        file_name=file_name,
        mime="application/json",
        use_container_width=True
    )

if __name__ == "__main__":
    main()


