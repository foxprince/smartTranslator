> 文件命名格式模板: core-concepts.md
> 文件路径: docs/product/

# [你的产品名称] 核心概念

## 文档信息
*   **创建日期**：[YYYY-MM-DD]
*   **最后更新**：[YYYY-MM-DD]
*   **作者**：[作者姓名/团队]
*   **状态**：[例如：草稿, 审查中, 已定稿]

## 目录
*   [自动生成或手动维护]

## 1. 概述
*   [简要介绍你的产品是什么，解决了什么核心问题。]
*   [说明本文档的目的：定义构成产品基础的核心概念与指导原则，为团队提供统一、清晰的理解。]

## 2. 核心理念 (可选, Core Philosophy)
*   (如果适用) 阐述产品背后的核心理念或哲学。
    *   理念点 1: 简短描述
    *   理念点 2: 简短描述
    *   ...

## 3. 核心原则 (可选, Core Principles)
*   (如果适用) 简要列出贯穿所有核心概念的指导原则。
    *   原则 1: 简短描述
    *   原则 2: 简短描述
    *   ...

## 4. 核心概念介绍

### 4.1 核心概念列表 (Core Concepts List)
*   列出产品的核心概念（通常 3-6 个为宜）。
    *   例如：[概念A], [概念B], [概念C]

### 4.2 核心概念详解 (Core Concepts Details)
*   接下来逐一详细介绍产品的核心概念。
*   对于每个概念：
    *   #### [概念名称 1]
        *   **定义**：清晰简洁地解释这个概念是什么。
        *   **特性**：列出该概念的关键属性、特点或规则。
        *   **示例**：提供 1-3 个具体的产品内示例，帮助理解。
        *   **(可选) 子类型/分类**：如果概念有不同的类型或子分类，在此说明。
    *   #### [概念名称 2]
        *   **定义**：...
        *   **特性**：...
        *   **示例**：...
    *   ... (继续列出所有核心概念)

## 5. 概念之间的关系
*   描述核心概念之间是如何相互连接和影响的。
*   **(推荐)** 使用图表（例如 Mermaid `graph TD` 或 `graph LR`）可视化这些关系。
    ```mermaid
    graph TD
        A[概念A] --> B[概念B]
        B --> C[概念C]
        C --> A
        B -- 描述 --> D[概念D]
    ```
*   **关系详解**：对图表中的连接或重要的概念间交互进行文字说明。解释数据如何流动，或者一个概念如何依赖/包含/导致另一个概念。

## 6. AI 辅助概念 (如果适用)
*   如果产品使用 AI，定义与 AI 相关的特定概念。
*   **[AI 概念 1，例如：智能建议]**
    *   **定义**：解释这个 AI 能力或概念是什么。
    *   **应用场景**：描述它在产品的哪些地方被使用，如何帮助用户。
*   **[AI 概念 2，例如：上下文感知]**
    *   **定义**：...
    *   **应用场景**：...
*   ... (继续列出所有相关的 AI 概念)

## 7. 核心概念在系统中的主要应用
*   将抽象的核心概念与产品的具体功能或模块联系起来。
*   ### [主要功能/模块名称 1]
    *   **应用的核心概念**：[概念 A], [概念 B]
    *   **简要说明**：描述这个功能如何体现或使用了列出的核心概念。
*   ### [主要功能/模块名称 2]
    *   **应用的核心概念**：[概念 C], [概念 D]
    *   **简要说明**：...
*   ... (继续列出主要功能及其关联的概念)

## 8. 总结
*   简要重申文档的重要性。
*   总结核心概念如何共同构成产品的骨架和逻辑。
*   强调拥有共同理解对团队协作的好处。
