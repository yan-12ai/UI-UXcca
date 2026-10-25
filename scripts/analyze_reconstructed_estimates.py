#!/usr/bin/env python3
"""Recalculate descriptive tables from retrospective estimates.

The input is not a recovered survey export. Results must remain labelled
retrospective estimates, not actual participant responses.
"""
from pathlib import Path
import csv, json, statistics
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "survey_data" / "reconstructed_estimates.json"

def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    questions, people = data["questions"], data["participants"]
    original, redesigned = data["original_estimates"], data["redesigned_estimates"]
    assert len(people) == 5 and len(questions) == 18
    assert all(len(row) == 18 for row in original + redesigned)
    assert all(type(v) is int and 1 <= v <= 10 for row in original + redesigned for v in row)
    average = statistics.mean
    long_rows = [["participant_id","participant_name","focus_theme","question_number","parameter","original_estimate","redesigned_estimate","estimated_difference","data_status"]]
    participant_rows = [["participant_id","participant_name","focus_theme","original_mean_estimate","redesigned_mean_estimate","mean_difference_estimate","data_status"]]
    for i, person in enumerate(people):
        for j, question in enumerate(questions):
            long_rows.append([person["id"],person["name"],person["focus"],j+1,question["parameter"],original[i][j],redesigned[i][j],redesigned[i][j]-original[i][j],"RETROSPECTIVE ESTIMATE — NOT ORIGINAL RESPONSE"])
        participant_rows.append([person["id"],person["name"],person["focus"],f"{average(original[i]):.2f}",f"{average(redesigned[i]):.2f}",f"{average([b-a for a,b in zip(original[i],redesigned[i])]):.2f}","RETROSPECTIVE ESTIMATE"])
    write_csv(ROOT/"survey_data"/"participant_ratings_estimated.csv", long_rows)
    write_csv(ROOT/"survey_data"/"participant_summary_estimated.csv", participant_rows)
    parameter_rows = [["question_number","parameter","n_estimated_pairs","original_mean_estimate","redesigned_mean_estimate","mean_difference_estimate","original_median_estimate","redesigned_median_estimate","data_status"]]
    for j, question in enumerate(questions):
        a, b = [row[j] for row in original], [row[j] for row in redesigned]
        parameter_rows.append([j+1,question["parameter"],5,f"{average(a):.2f}",f"{average(b):.2f}",f"{average([y-x for x,y in zip(a,b)]):.2f}",statistics.median(a),statistics.median(b),"RETROSPECTIVE ESTIMATE"])
    write_csv(ROOT/"survey_data"/"parameter_summary_estimated.csv", parameter_rows)
    distribution = [["website_version","score","rubric_label","item_count","percent_of_90_estimated_ratings","data_status"]]
    for version, matrix in [("Original",original),("Redesigned",redesigned)]:
        values = [v for row in matrix for v in row]
        for score in range(1,11):
            n = values.count(score)
            label = next((x["label"] for x in data["rating_scale"] if x["score"] == score), "")
            distribution.append([version,score,label,n,f"{n/len(values)*100:.1f}","RETROSPECTIVE ESTIMATE"])
    write_csv(ROOT/"survey_data"/"rating_distribution_estimated.csv", distribution)
    result = {
        "status":"RETROSPECTIVE ESTIMATES ONLY — NOT VERIFIED ORIGINAL SURVEY DATA",
        "participants":len(people),"parameters":len(questions),"estimated_item_pairs":len(people)*len(questions),
        "original_mean_estimate":round(average([v for row in original for v in row]),2),
        "redesigned_mean_estimate":round(average([v for row in redesigned for v in row]),2),
        "mean_difference_estimate":round(average([y-x for a,b in zip(original,redesigned) for x,y in zip(a,b)]),2),
        "note":data["reconstruction_note"]
    }
    (ROOT/"survey_data"/"overall_summary_estimated.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    main()
