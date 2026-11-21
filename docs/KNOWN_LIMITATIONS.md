# Known Limitations and Future Work

- The bundled dataset is ESCO v1.1.1 occupation classification data, not job vacancies or local labor-market listings. ESCO content requires attribution; the separate licence for the Tabiya CSV conversion is **Not verified**. There is no dated vacancy history for forecasting.
- Skill extraction uses a finite transparent dictionary. It does not infer skill proficiency.
- Matching uses lexical TF-IDF/cosine similarity; it is not a probability, hiring model, or validated ranking evaluation.
- Resume parsing extracts text only. Scanned PDF OCR and structured education/experience extraction are absent.
- The roadmap page is a dataset-derived checklist with progress tracking and documentation search suggestions; it is not a course plan.
- Career comparisons use standardized occupation profiles and linked skills. Curated occupation links are administrator maintained; inferred links are descriptive dataset relationships.
- No forecasting, live learning-provider catalog, email recovery, backup encryption, or model training/deployment is implemented. Backup/restore and account export/deletion are available locally.
- Layout uses Streamlit responsive behavior and has not had a separate mobile or WCAG audit.
