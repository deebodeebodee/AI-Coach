import os
import requests
import streamlit as st

st.set_page_config(page_title="AI Coach", layout="centered")

openrouter_api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

# ---------- Sample scored profiles ----------
SAMPLE_PROFILES = {
    "Profile A — Passion": {
        "name": "Alex",
        "trust": 3,
        "curiosity": 4,
        "passion": 2,
        "focus": "Passion",
        "summary": "Passion appears to be the current stretch area. The leader seems more comfortable with curiosity and day-to-day trust behaviours than visibly energising others around shared purpose.",
    },
    "Profile B — Curiosity": {
        "name": "Sam",
        "trust": 4,
        "curiosity": 2,
        "passion": 4,
        "focus": "Curiosity",
        "summary": "Curiosity appears to be the current stretch area. The leader may be dependable and committed, but less likely to pause, question assumptions, or explore different perspectives.",
    },
    "Profile C — Trust": {
        "name": "Jordan",
        "trust": 2,
        "curiosity": 4,
        "passion": 3,
        "focus": "Trust",
        "summary": "Trust appears to be the current stretch area. The leader may bring ideas and energy, but may need to work more intentionally on reliability, openness, and confidence-building with others.",
    },
}


def score_band(score):
    if score < 2.5:
        return "lower"
    elif score < 3.8:
        return "moderate"
    return "higher"


def build_context_block(trust_score, curiosity_score, passion_score, chosen_value, profile_name):
    trust_band = score_band(trust_score)
    curiosity_band = score_band(curiosity_score)
    passion_band = score_band(passion_score)

    return f"""
Assessment context from the leadership self-assessment:
- Trust score: {trust_score} ({trust_band})
- Curiosity score: {curiosity_score} ({curiosity_band})
- Passion score: {passion_score} ({passion_band})
- Selected value for reflection: {chosen_value}

Use these scores only as light developmental context.
Do not overstate what the scores mean.
Do not diagnose personality or capability.
Treat this as a developmental reflection conversation, not an evaluation.
"""


def fallback_feedback(chosen_value):
    if chosen_value == "Trust":
        return """
### What behaviour came through strongly
Your reflection suggests a genuine intention to be dependable and committed in your work. There are signs that you care about delivering and taking responsibility seriously.

### What may be missing or underused
What is less visible is whether trust is being built relationally, not just through effort. Trust often also involves transparency, inviting others in, and creating confidence rather than carrying everything alone.

### One next-step suggestion
The next time you feel pressure to take on more yourself, share the situation earlier with someone else and clarify what support or ownership can be distributed.

### Useful development route
If this feels like a real pattern, use it as a prompt to explore a relevant Telenor Academy resource or leadership development conversation focused on trust-building, delegation, and psychological safety.

### Conversation starter
You could bring this reflection into a conversation with your manager, supervisor, or programme facilitator and ask where greater trust-building behaviour would make the biggest difference.
"""
    elif chosen_value == "Curiosity":
        return """
### What behaviour came through strongly
Your reflection suggests awareness and engagement with what is happening around you. There are signs that you are noticing issues rather than ignoring them.

### What may be missing or underused
What is less visible is whether you explored alternatives, questioned assumptions, or stepped back to learn from the situation. Curiosity is not just noticing a problem, but actively examining it from different angles.

### One next-step suggestion
In a similar situation, ask yourself one additional question before reacting: what else might explain this, and what have I not considered yet?

### Useful development route
If this feels like a useful stretch area, look for a relevant Telenor Academy or leadership development resource that helps you practise experimentation, reflection, and learning in action.

### Conversation starter
You could use this reflection as a starting point for a development conversation about where more curiosity would improve your leadership decisions.
"""
    else:
        return """
### What behaviour came through strongly
Your reflection shows strong energy, commitment, and personal investment in the work. It suggests that you care deeply about getting things done and feel responsible for outcomes.

### What may be missing or underused
What may be less visible is whether this passion is being channelled in a sustainable and constructive way. Staying late every day may reflect commitment, but it can also suggest difficulty setting boundaries or maintaining long-term effectiveness.

### One next-step suggestion
Choose one opportunity this week to express why the work matters and invite another person into that sense of purpose, rather than carrying the energy alone.

### Useful development route
If this feels like a genuine development theme, explore whether a relevant Telenor Academy resource or leadership programme could help you practise translating personal commitment into shared energy and sustainable leadership.

### Conversation starter
You could use this reflection as an exploratory tool in a conversation with your manager or programme facilitator about how to turn individual drive into wider team motivation.
"""


def get_ai_feedback(chosen_value, example_text, trust_score, curiosity_score, passion_score, profile_name):
    context_block = build_context_block(
        trust_score,
        curiosity_score,
        passion_score,
        chosen_value,
        profile_name,
    )

    prompt = f"""
You are a supportive but evidence-aware developmental leadership reflection coach supporting Telenor leaders after a values-based self-assessment.

A leader has completed a self-assessment on three values: Trust, Curiosity, and Passion.
They have now come to the AI coach after viewing their report.

{context_block}

Leader's written reflection:
{example_text}

Your job is to help them reflect on how their real behaviour lines up with the chosen value.

Give your answer in exactly this structure:

### What behaviour came through strongly
Write 2-4 sentences. Identify the strongest visible leadership behaviours in the example.

### What may be missing or underused
Write 2-4 sentences. Point out what is not yet visible, underdeveloped, or could be strengthened.
Use gentle, developmental language.

### One next-step suggestion
Give 1 practical action they could try next time.

### Useful development route
Suggest one useful route such as an existing leadership programme, Telenor Academy resource, or a reflective development conversation with a manager, supervisor, or facilitator.
Keep it light and exploratory.

### Conversation starter
Give 1 short suggestion for how they could use this output to start a development conversation.

Rules:
- Be constructive, specific, and developmental
- Do not sound clinical, generic, or harsh
- Focus on behaviour, not fixed traits
- Refer lightly to the score context when useful, but do not over-rely on it
- Do not imply the score is fully accurate or diagnostic
- Encourage the leader to use the output as an exploratory tool, not a final judgement
- Keep the total answer concise and readable
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "AI Reflection Coach Prototype",
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a supportive developmental leadership coach.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            },
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception:
        return fallback_feedback(chosen_value)


st.title("AI Coach")
st.caption("Prototype: post-report reflection coach for Trust, Curiosity, and Passion")

st.markdown(
    """
This prototype is designed to sit after the leadership self reflection.
A leader reviews their profile, chooses one value to reflect on, and then receives developmental coaching feedback on a real example from work.
"""
)

st.subheader("1) Select a sample scored profile")
selected_profile_label = st.selectbox(
    "Choose a sample leadership profile",
    list(SAMPLE_PROFILES.keys()),
)

profile = SAMPLE_PROFILES[selected_profile_label]
trust_score = profile["trust"]
curiosity_score = profile["curiosity"]
passion_score = profile["passion"]
default_focus = profile["focus"]

st.caption("For prototyping purposes, scored profiles are simulated to demonstrate the report-to-coach handoff.")

st.subheader("2) Selected report summary")
summary_cols = st.columns(3)
summary_cols[0].metric("Trust", trust_score)
summary_cols[1].metric("Curiosity", curiosity_score)
summary_cols[2].metric("Passion", passion_score)

st.info(profile["summary"])

allowed_values = ["Trust", "Curiosity", "Passion"]
value = st.selectbox(
    "2) Choose the value to reflect on",
    allowed_values,
    index=allowed_values.index(default_focus),
)

st.info(
    f"The AI coach will focus on **{value}** while using the three scores only as light developmental context."
)

prompt_map = {
    "Trust": "Describe a recent time when you showed Trust at work.",
    "Curiosity": "Describe a recent time when you showed Curiosity at work.",
    "Passion": "Describe a recent time when you showed Passion at work.",
}

example_defaults = {
    "Trust": "For example: I made a point of following through on what I had promised the team and checked in openly when delays came up.",
    "Curiosity": "For example: I paused before deciding, asked what I might be missing, and invited another perspective before moving forward.",
    "Passion": "For example: I made extra effort on a project because I cared about the outcome, but I am not sure whether I made that purpose visible to others.",
}

st.subheader("3) Write a recent example")
example = st.text_area(
    prompt_map[value],
    height=220,
    placeholder=example_defaults[value],
)

st.subheader("4) Get developmental feedback")

if st.button("Generate AI coaching feedback"):
    if not openrouter_api_key:
        st.error("No OpenRouter API key found. Set OPENROUTER_API_KEY in your terminal first.")
    elif not example.strip():
        st.warning("Please enter a short example first.")
    else:
        with st.spinner("Generating feedback..."):
            feedback = get_ai_feedback(
                value,
                example,
                trust_score,
                curiosity_score,
                passion_score,
                leader_name,
            )
            st.markdown(feedback)

st.divider()
st.subheader("How this could connect to Microsoft Forms")
st.markdown(
    """
**Prototype logic:**
- Microsoft Forms collects the self-reflection responses
- a report page calculates or displays Trust, Curiosity, and Passion scores
- the report then opens this coach with those values passed in

**Simple prototype handoff idea:**
A report page could pass the scored values and suggested reflection focus into the coach automatically.
"""
)

st.markdown(
    "**Prototype note:** This version uses OpenRouter's free models router where available, with a fallback developmental response if the live model is unavailable."
)
