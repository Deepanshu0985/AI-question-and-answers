
def merge_models(data, output_excel_path="mismatched_topics.xlsx"):
    merged_output = {}
    mismatch_records = []

    models = list(data.keys())  # e.g. ["phi4", "gpt-oss"]

    for subject in data[models[0]]:
        merged_output[subject] = {"setA": {}}

        model1_questions = data[models[0]][subject]
        model2_questions = data[models[1]][subject]

        for q1, q2 in zip(model1_questions, model2_questions):
            qid = int(q1["question_id"])
            question_text = q1.get("question", "")

            # ✅ Filter topics with value > 0
            topics1 = {k: v for k, v in q1["topic_vector"].items() if v > 0}
            topics2 = {k: v for k, v in q2["topic_vector"].items() if v > 0}

            topic_names1 = list(topics1.keys())
            topic_names2 = list(topics2.keys())

            if topic_names1 == topic_names2:
                merged_output[subject]["setA"][qid] = topics1
            else:
                # merge both, equal weight per unique topic
                all_topics = set(topic_names1 + topic_names2)
                merged_topics = {}
                split_percent = round(100 / len(all_topics), 2) if all_topics else 0
                for topic in all_topics:
                    merged_topics[topic] = split_percent

                merged_output[subject]["setA"][qid] = merged_topics

                # Record mismatch
                mismatch_records.append({
                    "Subject": subject,
                    "Question ID": qid,
                    "Question": question_text,
                    "Model 1 Topics": ", ".join(topic_names1),
                    "Model 2 Topics": ", ".join(topic_names2),
                    "Merged Topics": ", ".join(merged_topics.keys())
                })
    return merged_output  # ✅ returns dict, keeps int keys


# final_result = merge_models(data)
# final_result = json.dumps(final_result, ensure_ascii=False, indent=2)
# print(final_result)
