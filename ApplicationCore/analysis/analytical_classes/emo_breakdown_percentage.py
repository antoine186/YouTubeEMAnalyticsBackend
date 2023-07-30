class EmoBreakdownPercentage:
    def __init__(self, sadness_percentage, joy_percentage, disgust_percentage, anger_percentage,
                 fear_percentage, surprise_percentage, neutral_percentage) -> None:
        self.sadness_percentage = sadness_percentage
        self.joy_percentage = joy_percentage
        self.disgust_percentage = disgust_percentage
        self.anger_percentage = anger_percentage
        self.fear_percentage = fear_percentage
        self.surprise_percentage = surprise_percentage
        self.neutral_percentage = neutral_percentage

    def get_emo_breakdown_percentage(self):
        emo_percentages_dict = {
            "sadness": { "percentage": self.sadness_percentage},
            "joy": { "percentage": self.joy_percentage},
            "disgust": { "percentage": self.disgust_percentage},
            "anger": { "percentage": self.anger_percentage},
            "fear": { "percentage": self.fear_percentage},
            "surprise": { "percentage": self.surprise_percentage},
            "neutral": { "percentage": self.neutral_percentage}
        }

        return emo_percentages_dict

"""
sadness 😢
joy 😃
love 🥰
disgust 🤢
anger 😡
fear 😱
surprise 😯
neutral 😐
"""