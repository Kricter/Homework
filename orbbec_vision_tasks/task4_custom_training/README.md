# TASK4: 自定义物体训练（耳塞盒）

## 训练流程
```bash
cd scripts

# 1. 交互打标
python3 label_tool.py

# 2. 数据增强（40 → 440 张）
python3 augment.py

# 3. 训练
python3 train_v3.py

# 4. 训练好的模型 → trained_model.pt
```

## 文件说明
| 文件 | 说明 |
|------|------|
| dataset/dataset.yaml | 基础数据集配置 |
| dataset/dataset_aug.yaml | 增强数据集配置 |
| dataset/classes.txt | 类别名 |
| scripts/label_tool.py | 鼠标画框打标工具 |
| scripts/augment.py | 离线数据增强 |
| scripts/train.py | 基础训练 v1 |
| scripts/train_v2.py | 增强训练 v2 |
| scripts/train_v3.py | 440 张增强数据训练 v3 |
| trained_model.pt | 训练好的模型（93%+） |

## 效果
- 耳塞盒检测置信度: 93%+
- 螺丝帽误检置信度: ~0.70（被 0.90 阈值过滤）
