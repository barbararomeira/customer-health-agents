# 3. Reading tone (the "sentiment" part)

The obvious approach is sentiment analysis: score each call from −1 to +1 and alert when it drops.
We didn't do that. Here's why, and what we did instead.

## Why an absolute sentiment score fails here

1. **Problem-solving calls sound negative.** A call about wrong counts and a camera angle is full of
   negative words, and it's often a healthy call: the customer cares enough to fix it.
2. **Some teams are terse in every call.** Neutral, short, no small talk. Scored on an absolute
   scale, they're flagged every week for their culture, while the customer whose warm calls went
   curt never crosses the threshold.
3. **Politeness hides decisions.** "That's interesting, we'll think about it after the budget
   review" scores as positive and is one of the strongest risk signals there is.
4. **A score loses the quote.** The board needs the sentence that shows the risk, not a number.

## What we did instead: compare the customer with themselves

**Tone is judged against the same customer's earlier calls.** The question is never "is this call
negative?" It's "is this customer different from how they usually are?"

The markers the reader looks for, all relative to that customer's baseline:

| Marker | Example |
|---|---|
| Their share of talking drops | The plant manager used to drive the call; now our side talks 80% of it |
| Shorter answers, fewer questions | "Fine." "OK." "No questions." |
| Deferring language | "We'll see." "After the budget review." "Not a priority this month." |
| Frustration words | "again", "still", "every week" |
| A sudden shift to formal tone | First names and jokes, then "as per our agreement" |
| Sarcasm | "Great, another report." |
| The decision maker stops speaking | Still invited, no longer says anything |

## Who said it matters

- **Attribute every line to a speaker**, and separate our side from theirs. Our own team's
  frustration on a call isn't a customer signal.
- **Rank the speakers.** A line supervisor's complaint and an operations director's complaint are
  different signals. The sponsor going quiet matters more than anything else in this table.
- **Relayed statements are marked as relayed.** "The engineer told me after the call that
  procurement is asking about licences" is real and useful, but you can't check it by opening a
  call. It can make yellow, never red alone.

## Duration matters more than intensity

One bad call is noise. The rules only let a tone signal count toward red after it has lasted
**three weeks of a four-week window**. A trend younger than that is yellow: worth watching, not
worth an escalation.

## Every claim carries a verbatim quote

The reader quotes the customer's exact words with a link to the moment in the call. Never a
paraphrase dressed as a quote. This is what makes the board trustworthy: anyone who doubts a red
can open the call and hear it.

## Why a language model, not a classifier

The judgement needed here ("is this deferring language, or honest scheduling?", "is this terse
because they're annoyed, or because they always are?") needs the whole call and the customer's
history in view. A per-sentence sentiment classifier sees neither. A model reading the full
transcript next to earlier calls can, as long as:

- it reads **full transcripts, not summaries** (summaries drop exactly the hedges that matter),
- it's given the **customer's earlier calls** as the baseline,
- it must **quote** every claim, and
- a stronger model **re-checks every red** against the transcript before anyone sees it.

## Open questions

- How many earlier calls make a baseline? We used "whatever exists in the last few months". With
  only one or two calls, tone shouldn't be used at all.
- Language: many customers speak a second language on calls. Shorter answers can be fluency, not
  mood. The baseline helps, because it's the same speaker, but it doesn't fully solve this.
- Should talk-share be measured (speaker time from the transcript) rather than judged? It would be
  cheap and objective, and it's the most likely next addition.
