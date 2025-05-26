import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Title
st.title("Alumni Engagement Score Compiler")
st.markdown("Upload each of the four CSV files corresponding to alumni engagement types.")

# File uploaders
communication_file = st.file_uploader("Upload Communication CSV", type=["csv"])
experiential_file = st.file_uploader("Upload Experiential CSV", type=["csv"])
volunteer_file = st.file_uploader("Upload Volunteer CSV", type=["csv"])
philanthropic_file = st.file_uploader("Upload Philanthropic CSV", type=["csv"])

# Function to process files and generate the final Excel output
def process_files(files_info):
    today_date = datetime.today().strftime('%Y-%m-%d')
    score_data = {}
    all_ids = set()

    for quality, file in files_info.items():
        if file is not None:
            df = pd.read_csv(file, header=None, names=["ID"])
            counts = df["ID"].value_counts().to_dict()

            if quality == "Philanthropic":
                scores = {id_: 10 for id_ in counts.keys()}
            else:
                scores = {id_: min(count, 10) for id_, count in counts.items()}

            score_data[quality] = scores
            all_ids.update(scores.keys())

    rows = []
    for id_ in all_ids:
        for quality in files_info.keys():
            score = score_data.get(quality, {}).get(id_, 0)
            rows.append({
                "ID": id_,
                "date of entry": today_date,
                "source": f"AEM-{quality}",
                "type": f"AEM {quality}",
                "description": score
            })

    final_df = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        final_df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Process and display download button
if st.button("Generate Engagement File"):
    if all([communication_file, experiential_file, volunteer_file, philanthropic_file]):
        files_info = {
            "Communication": communication_file,
            "Experiential": experiential_file,
            "Volunteer": volunteer_file,
            "Philanthropic": philanthropic_file
        }
        output = process_files(files_info)
        st.success("✅ File processed successfully!")
        st.download_button(
            label="Download Compiled Excel",
            data=output,
            file_name="Engagement_Scores_Compiled.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("❌ Please upload all four required files before generating the output.")
