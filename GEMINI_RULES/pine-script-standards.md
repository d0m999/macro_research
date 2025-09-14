---
inclusion: manual
---

# Pine Script v6 常见错误规避指南 📊

Pine Script v6 — Authoring Rules (upload as rules.md)



A compact checklist to avoid common compiler/runtime pitfalls when asking AI to write Pine.

Target: TradingView Pine Script v6.



1\) Golden rules


No side-effect calls in local scope. Only call plot, plotshape, plotchar, barcolor, bgcolor, hline, fill, alertcondition, label.new, line.new, box.new, table.\* at top level (not inside if/for/while/switch).



Compute first, draw later. Put conditions/results into series variables; then make a single top-level draw call.



Avoid forward-looking bias. Use current bar values only; update rolling baselines after barstate.isconfirmed.



Pattern



cond = close > open

col  = cond ? color.green : na

barcolor(col)  // top-level only



2\) MTF / request.security



Do not set timeframe= or timeframe\_gaps= in indicator() when the script produces side effects (drawings/alerts).



For multi-timeframe inputs, use request.security(tf, expr) where expr is pure (no side effects).



Never draw inside security expressions. Compute in HTF, draw in the current TF.



Pattern



htfRsi = request.security(syminfo.tickerid, "60", ta.rsi(close, 14))

plot(htfRsi)  // draw in current TF



3\) Syntax \& formatting (to prevent “end of line without line continuation”)



Do not break ternary ?: across lines. If long, use if/else or compute into temp vars.



Keep function arguments on one line (or precompute variables); avoid nested multi-line ternaries inside calls.



Respect indentation: each new block requires consistent indentation; close all blocks.



Bad



fmt(v) =>

&nbsp;   v > 1e6 ? "M" :

&nbsp;   v > 1e3 ? "K" :

&nbsp;   "x"        // multiline ternaries -> brittle



Good



fmt(v) =>

&nbsp;   string out = ""

&nbsp;   if v > 1e6

&nbsp;       out := "M"

&nbsp;   else if v > 1e3

&nbsp;       out := "K"

&nbsp;   else

&nbsp;       out := "x"

&nbsp;   out



4\) Visualization rules



Top-level drawing only (see §1). To conditionally color, pass a series color to plot()/barcolor().



plot() with style=plot.style\_histogram has one UI color; to force multi-color, set color=series.



Use offset only to shift known values; it does not predict future bars.



hline and fill must be declared once at top level.



Pattern



histColor = condHigh ? color.green : condLow ? color.red : color.new(color.gray,50)

plot(value, style=plot.style\_histogram, color=histColor)



5\) Repainting \& confirmation



Avoid security(..., lookahead=barmerge.lookahead\_on) unless you want repaint.



Use barstate.isrealtime/barstate.isconfirmed to separate real-time updates from confirmed values.



When building baselines/EMAs, update on confirmed bars to prevent look-ahead bias.



6\) Tables / drawings



table.new creates a floating panel (not time-anchored). Refresh in if barstate.islast.



For stability, compute text/colors in variables, then call table.cell(...) in single-line form.



Keep table size reasonable (e.g., 7×24 heatmaps are fine).



7\) Arrays \& state



Initialize globals once with var.



Never assume an array slot is initialized—na-check before use.



For rolling stats per bucket (e.g., 168 hour-of-week slots), store baselines and counters in parallel arrays and update post-confirmation.



Pattern



var baselines = array.new\_float(168, na)

var counts    = array.new\_int(168, 0)



slot   = (dayofweek(time) - 1) \* 24 + hour(time)

oldB   = array.get(baselines, slot)

alpha  = 2.0 / (len + 1.0)

newB   = na(oldB) ? volume : oldB + alpha\*(volume - oldB)

if barstate.isconfirmed

&nbsp;   array.set(baselines, slot, newB)

&nbsp;   array.set(counts, slot, array.get(counts, slot) + 1)



8\) Alerts



alertcondition() must be top-level.



Keep alert expressions pure (boolean series). Compute complex logic first, then reference in a single alertcondition.



9\) Strategy vs Indicator



Use indicator() for signals/visuals; use strategy() only when placing orders.



Strategy order functions (strategy.entry, etc.) are side effects—keep them out of security expressions and local scopes.



10\) Performance \& limits



Prefer ta.\* functions over custom loops when possible.



Limit heavy per-bar loops; precompute thresholds; avoid large per-bar table rebuilds except under barstate.islast.



Mind built-in limits (plots, labels, lines per script).



11\) Testing checklist (copy into every task)







12\) Minimal safe templates



Conditional bar color



//@version=6

indicator("Template: Conditional Color", overlay=true)

cond = close > open

col  = cond ? color.new(color.green,0) : na

barcolor(col)



HTF input, LTF drawing



//@version=6

indicator("Template: HTF RSI", overlay=false)

htfRsi = request.security(syminfo.tickerid, "60", ta.rsi(close,14))

plot(htfRsi)



Table heatmap skeleton



//@version=6

indicator("Template: 7x24 Heatmap", overlay=true)

var tbl = table.new(position.top\_right, 7, 25)

if barstate.islast

&nbsp;   table.cell(tbl, 0, 0, "Mon")

&nbsp;   // ... fill cells via single-line table.cell calls

