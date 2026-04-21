---
name: calculator
description: Use this skill when the user needs precise arithmetic, discounts, ratios, percentages, or other numeric calculations. Always call the calculate_math tool instead of doing mental math.
allowed-tools: calculate_math
---

# 數學計算技能

這項技能專門處理需要精確數值運算的任務。

## 何時使用此技能
當使用者請你幫忙算數學，例如大數字的加減乘除、折扣、比例、百分比或一般算式時，請使用這項技能。

## 執行準則
1. **不要靠自己算**：語言模型不擅長精確運算，必須呼叫註冊好的 `calculate_math` 工具。
2. **先整理算式**：從使用者的口語問題中提煉出正確的數學表達式，再交給工具執行。
3. **回覆要能理解**：提供結果時，順便用白話文說明計算邏輯。
