from dash import dcc, html, register_page

register_page(__name__,
              path="/",
              order=0)


## Layout

layout = html.Div(
    [
        html.H1("Speed Reading Training"),
        dcc.Markdown(
            """
This app trains you to read faster and more effectively through a series of progressive exercises.

**How to get started**

1. Go to the **Text input** page and select a text file to work with.
2. Pick an exercise below and follow its instructions.
3. Save your performance at the end of each session.
4. Track your progress over time in the **Past performance** page.

---

**Exercises**

| # | Name | What it trains |
|---|------|----------------|
| 0 | Free Read | Baseline reading speed — read at your natural pace, timed |
| 1 | Block Read | Chunked reading — absorb N words at a time at a set pace |
| 2 | Word Search | Skimming — scan a full text rapidly to locate a target word |
| 3 | Peripheral Vision | Gaze control — find numbers or words using only peripheral vision |

---

*Start with **Free Read** to establish your baseline, then use the other exercises to push your limits.*
            """,
            style={"width": "70%"},
        ),
    ]
)


## Callbacks   