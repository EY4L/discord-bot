from random import choice

ANSWERS = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
    "Certainly no.",
    "Gods say yes.",
    "Gods say no.",
    "No one knows.",
    "I don't think so.",
    "You should go to Ye Olde and think about it.",
    "Ask Joe, I don't fucking know...",
]


def eight_ball_answer() -> str:
    """Generates a magic 8 ball answer to a user's question.

    Returns:
        str: 8 ball answer
    """
    return choice(ANSWERS)
