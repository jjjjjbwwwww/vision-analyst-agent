# 离线评测与反思机制

## 评测目标

评估不同 Agent 策略对输出质量的影响。

---

## 使用的指标

- bad：不合理 / 错误回答比例
- rep：重复度
- summary_ok：是否形成有效总结

---

## 对比策略

- baseline：无反思
- naive_reflect：始终反思
- gated_reflect：条件触发反思

---

## 结论

并非“更多思考 = 更好结果”，合理的 Gate 更重要。