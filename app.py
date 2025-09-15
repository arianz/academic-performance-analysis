import streamlit as st
import pandas as pd
import plotly.express as px

# Language selection
language = st.selectbox("Pilih Bahasa / Select Language", ["Bahasa Indonesia", "English"])

# Define labels based on language
if language == "English":
    title = "College Grades Analysis"
    bar_subheader = "Bar Chart: GPA per Semester"
    table_subheader1 = "Table: Courses per Semester"
    table_subheader2 = "Table: Courses per Grade"
    pie_subheader = "Pie Chart: Grade Distribution"
    semester_label = "Semester"
    gpa_label = "GPA"
    courses_label = "Courses"
    credits_label = "Credits"
    grade_label = "Grade"
    count_label = "Count"
    total_credits_label = "Total Credits"
    total_gpa_label = "Cumulative GPA"
    course_column = "Nama Mata Kuliah B. Inggris"
    error_file_not_found = "File 'grades.csv' not found!"
    warning_invalid_grades = "Invalid grades found: {}"
    warning_invalid_sks = "Invalid SKS values found in {} rows"
    warning_missing_grades = "Missing grades found in {} rows"
else:
    title = "Analisis Data Nilai Kuliah"
    bar_subheader = "Bar Chart: IPK per Semester"
    table_subheader1 = "Tabel: Mata Kuliah per Semester"
    table_subheader2 = "Tabel: Mata Kuliah per Nilai"
    pie_subheader = "Pie Chart: Distribusi Nilai Mata Kuliah"
    semester_label = "Semester"
    gpa_label = "IPK"
    courses_label = "Mata Kuliah"
    credits_label = "SKS"
    grade_label = "Nilai"
    count_label = "Jumlah"
    total_credits_label = "Total SKS"
    total_gpa_label = "IPK Kumulatif"
    course_column = "Mata Kuliah"
    error_file_not_found = "File 'grades.csv' tidak ditemukan!"
    warning_invalid_grades = "Nilai tidak valid ditemukan: {}"
    warning_invalid_sks = "Nilai SKS tidak valid ditemukan di {} baris"
    warning_missing_grades = "Nilai kosong ditemukan di {} baris"

# Read data from CSV
try:
    df = pd.read_csv('grades.csv')
except FileNotFoundError:
    st.error(error_file_not_found)
    st.stop()

# Mapping grades to numeric values
nilai_map = {
    'A': 4.0,
    'AB': 3.5,
    'B': 3.0,
    'BC': 2.5,
    'C': 2.0,
    'D': 1.5,
    'E': 1.0
}

# Validate grades
invalid_grades = df[~df['Nilai'].isin(nilai_map.keys())]['Nilai'].unique()
if len(invalid_grades) > 0:
    st.warning(warning_invalid_grades.format(invalid_grades))

# Check for missing grades
missing_grades = df['Nilai'].isna().sum()
if missing_grades > 0:
    st.warning(warning_missing_grades.format(missing_grades))

# Convert SKS to numeric
df['SKS'] = pd.to_numeric(df['SKS'], errors='coerce')

# Check for invalid SKS
invalid_sks = df['SKS'].isna().sum()
if invalid_sks > 0:
    st.warning(warning_invalid_sks.format(invalid_sks))

# Calculate numeric grade and weighted score
df['Nilai Numerik'] = df['Nilai'].map(nilai_map)
df['Bobot'] = df['Nilai Numerik'] * df['SKS']

# Calculate Total SKS and Cumulative GPA
total_sks = df['SKS'].sum()
total_bobot = df['Bobot'].sum()
cumulative_gpa = round(total_bobot / total_sks, 2) if total_sks > 0 else 0.0

# Group by semester for total credits and GPA
grouped = df.groupby('Semester').agg(
    total_sks=('SKS', 'sum'),
    total_bobot=('Bobot', 'sum')
).reset_index()
grouped['IPK'] = round(grouped['total_bobot'] / grouped['total_sks'], 2)

# Streamlit App
st.title(title)

# Display Total SKS and Cumulative GPA
st.subheader("Ringkasan Akademik" if language == "Bahasa Indonesia" else "Academic Summary")
col1, col2 = st.columns(2)
col1.metric(total_credits_label, total_sks)
col2.metric(total_gpa_label, f"{cumulative_gpa:.2f}")

# Bar Chart: GPA per Semester
st.subheader(bar_subheader)
fig_bar = px.bar(grouped, x='Semester', y='IPK', 
                 labels={'IPK': gpa_label, 'Semester': semester_label, 'total_sks': total_credits_label},
                 color='IPK',
                 color_continuous_scale='Blues',
                 text='IPK',
                 hover_data={'total_sks': True})

fig_bar.add_trace(
    px.line(grouped, x='Semester', y='IPK', 
            labels={'IPK': gpa_label, 'Semester': semester_label},
            color_discrete_sequence=['red']).data[0]
)
fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside', selector=dict(type='bar'))
fig_bar.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent
    font_color='black',
)
st.plotly_chart(fig_bar, use_container_width=True)

# Table: Courses per Semester with expander
st.subheader(table_subheader1)
grouped_semester = df.groupby('Semester')[[course_column, 'SKS']].apply(lambda x: x.reset_index(drop=True)).reset_index()
for semester, group in grouped_semester.groupby('Semester'):
    with st.expander(f"{semester_label}: {semester} ({len(group)} {courses_label})"):
        mata_kuliah_df = group[[course_column, 'SKS']].reset_index(drop=True)
        mata_kuliah_df.index += 1  # Start index from 1
        mata_kuliah_df.columns = [courses_label, credits_label]
        
        # Simple styling
        styled_df = mata_kuliah_df.style.set_properties(**{'border': '1px solid lightgray', 'padding': '10px'}) \
                                        .set_table_styles([{'selector': 'th', 'props': [('background-color', '#f0f0f0'), ('text-align', 'left')]}])
        st.dataframe(styled_df, use_container_width=True)

# Pie Chart: Grade Distribution
st.subheader(pie_subheader)
nilai_counts = df['Nilai'].value_counts().reset_index(name=count_label)
nilai_counts.columns = [grade_label, count_label]
fig_pie = px.pie(nilai_counts, values=count_label, names=grade_label, 
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 hole=0.3)
fig_pie.update_traces(textinfo='percent')
st.plotly_chart(fig_pie, use_container_width=True)

# Table: Courses per Grade with expander
st.subheader(table_subheader2)
grouped_nilai = df.groupby('Nilai')[course_column].apply(list).reset_index(name=courses_label)
for index, row in grouped_nilai.iterrows():
    with st.expander(f"{grade_label}: {row['Nilai']} ({len(row[courses_label])} {courses_label})"):
        mata_kuliah_df = pd.DataFrame(row[courses_label], columns=[courses_label])
        mata_kuliah_df.index += 1  # Start index from 1
        
        # Simple styling
        styled_df = mata_kuliah_df.style.set_properties(**{'border': '1px solid lightgray', 'padding': '10px'}) \
                                        .set_table_styles([{'selector': 'th', 'props': [('background-color', '#f0f0f0'), ('text-align', 'left')]}])
        st.dataframe(styled_df, use_container_width=True)