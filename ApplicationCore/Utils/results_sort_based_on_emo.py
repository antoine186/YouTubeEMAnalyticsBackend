
def results_sort_based_on_emo(emo_breakdown_results, emo_percentage):
    emo_breakdown_results.sort(key=lambda emo_breakdown_result: emo_breakdown_result.emo_breakdown.__dict__[emo_percentage], reverse = True)

    return emo_breakdown_results[:5]
