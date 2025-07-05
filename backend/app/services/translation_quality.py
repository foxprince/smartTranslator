"""
翻译质量评估服务
"""
import re
import math
from typing import List, Dict, Tuple
from ..schemas.translation import QualityScore, QualityLevel


class QualityAssessor:
    """翻译质量评估器"""
    
    def __init__(self):
        # 质量评估权重
        self.weights = {
            'length': 0.25,
            'consistency': 0.35,
            'language': 0.25,
            'structure': 0.15
        }
        
        # 语言检测模式
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        self.english_pattern = re.compile(r'[a-zA-Z]')
        
        # 常见翻译错误模式
        self.error_patterns = {
            'incomplete': [
                r'\[翻译失败',
                r'Translation failed',
                r'I cannot',
                r'I apologize',
                r'As an AI'
            ],
            'formatting': [
                r'^\s*$',  # 空白
                r'^[.。,，!！?？]+$',  # 只有标点
            ]
        }
    
    async def assess_batch(
        self, 
        source_texts: List[str], 
        translations: List[str]
    ) -> List[QualityScore]:
        """
        批量质量评估
        
        Args:
            source_texts: 源文本列表
            translations: 翻译文本列表
            
        Returns:
            List[QualityScore]: 质量评分列表
        """
        scores = []
        
        for source, translation in zip(source_texts, translations):
            score = await self.assess_single(source, translation)
            scores.append(score)
        
        return scores
    
    async def assess_single(self, source_text: str, translation: str) -> QualityScore:
        """
        单个翻译质量评估
        
        Args:
            source_text: 源文本
            translation: 翻译文本
            
        Returns:
            QualityScore: 质量评分
        """
        # 1. 长度合理性评估
        length_score = self._assess_length_reasonableness(source_text, translation)
        
        # 2. 一致性评估
        consistency_score = self._assess_consistency(source_text, translation)
        
        # 3. 语言准确性评估
        language_score = self._assess_language_accuracy(translation)
        
        # 4. 结构保持评估
        structure_score = self._assess_structure_preservation(source_text, translation)
        
        # 5. 计算综合评分
        overall_score = (
            length_score * self.weights['length'] +
            consistency_score * self.weights['consistency'] +
            language_score * self.weights['language'] +
            structure_score * self.weights['structure']
        )
        
        # 6. 检测问题
        issues = self._detect_issues(source_text, translation)
        
        # 7. 确定置信度等级
        confidence_level = self._get_confidence_level(overall_score)
        
        return QualityScore(
            overall_score=overall_score,
            length_score=length_score,
            consistency_score=consistency_score,
            language_score=language_score,
            confidence_level=confidence_level,
            issues=issues
        )
    
    def _assess_length_reasonableness(self, source: str, translation: str) -> float:
        """评估长度合理性"""
        if not source or not translation:
            return 0.0 if not translation else 1.0
        
        source_len = len(source.strip())
        translation_len = len(translation.strip())
        
        if source_len == 0:
            return 0.5
        
        # 计算长度比例
        ratio = translation_len / source_len
        
        # 不同语言对的合理长度比例范围
        if self._is_english_to_chinese(source, translation):
            # 英译中，中文通常比英文短
            ideal_range = (0.4, 1.2)
        elif self._is_chinese_to_english(source, translation):
            # 中译英，英文通常比中文长
            ideal_range = (0.8, 2.0)
        else:
            # 其他语言对，使用通用范围
            ideal_range = (0.5, 1.8)
        
        # 计算分数
        if ideal_range[0] <= ratio <= ideal_range[1]:
            return 1.0
        elif ratio < ideal_range[0]:
            # 翻译过短
            return max(0.0, ratio / ideal_range[0])
        else:
            # 翻译过长
            return max(0.0, ideal_range[1] / ratio)
    
    def _assess_consistency(self, source: str, translation: str) -> float:
        """评估翻译一致性"""
        if not source or not translation:
            return 0.0
        
        consistency_score = 1.0
        
        # 检查是否保持了数字
        source_numbers = re.findall(r'\d+', source)
        translation_numbers = re.findall(r'\d+', translation)
        
        if source_numbers and not translation_numbers:
            consistency_score -= 0.3
        elif len(source_numbers) != len(translation_numbers):
            consistency_score -= 0.2
        
        # 检查是否保持了专有名词（大写字母开头的词）
        source_proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+\b', source)
        translation_proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+\b', translation)
        
        if source_proper_nouns and len(translation_proper_nouns) < len(source_proper_nouns) * 0.5:
            consistency_score -= 0.2
        
        # 检查标点符号的合理使用
        source_punct_count = len(re.findall(r'[.!?。！？]', source))
        translation_punct_count = len(re.findall(r'[.!?。！？]', translation))
        
        if source_punct_count > 0 and translation_punct_count == 0:
            consistency_score -= 0.1
        
        return max(0.0, consistency_score)
    
    def _assess_language_accuracy(self, translation: str) -> float:
        """评估语言准确性"""
        if not translation:
            return 0.0
        
        # 检查是否包含明显的错误标志
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, translation, re.IGNORECASE):
                    if error_type == 'incomplete':
                        return 0.0
                    elif error_type == 'formatting':
                        return 0.2
        
        # 检查语言的一致性（不应该混合多种语言）
        chinese_chars = len(self.chinese_pattern.findall(translation))
        english_chars = len(self.english_pattern.findall(translation))
        total_chars = len(translation.replace(' ', ''))
        
        if total_chars == 0:
            return 0.0
        
        # 计算主要语言的比例
        if chinese_chars > 0 and english_chars > 0:
            # 混合语言，检查是否合理
            chinese_ratio = chinese_chars / total_chars
            english_ratio = english_chars / total_chars
            
            # 如果一种语言占主导地位（>70%），认为是合理的
            if max(chinese_ratio, english_ratio) > 0.7:
                return 0.9
            else:
                return 0.6  # 语言混合过多
        
        return 1.0  # 单一语言，认为是好的
    
    def _assess_structure_preservation(self, source: str, translation: str) -> float:
        """评估结构保持"""
        if not source or not translation:
            return 0.0
        
        structure_score = 1.0
        
        # 检查行数是否保持
        source_lines = source.count('\n')
        translation_lines = translation.count('\n')
        
        if source_lines != translation_lines:
            structure_score -= 0.3
        
        # 检查段落结构（连续的换行符）
        source_paragraphs = len(re.split(r'\n\s*\n', source.strip()))
        translation_paragraphs = len(re.split(r'\n\s*\n', translation.strip()))
        
        if abs(source_paragraphs - translation_paragraphs) > 1:
            structure_score -= 0.2
        
        # 检查是否保持了列表结构
        source_list_items = len(re.findall(r'^\s*[-*•]\s', source, re.MULTILINE))
        translation_list_items = len(re.findall(r'^\s*[-*•]\s', translation, re.MULTILINE))
        
        if source_list_items > 0 and translation_list_items == 0:
            structure_score -= 0.2
        
        return max(0.0, structure_score)
    
    def _detect_issues(self, source: str, translation: str) -> List[str]:
        """检测翻译问题"""
        issues = []
        
        # 检查是否为空翻译
        if not translation or not translation.strip():
            issues.append("翻译结果为空")
            return issues
        
        # 检查是否包含错误标志
        for pattern in self.error_patterns['incomplete']:
            if re.search(pattern, translation, re.IGNORECASE):
                issues.append("翻译不完整或包含错误信息")
                break
        
        # 检查长度异常
        if source and translation:
            ratio = len(translation) / len(source)
            if ratio < 0.2:
                issues.append("翻译过短，可能不完整")
            elif ratio > 3.0:
                issues.append("翻译过长，可能包含冗余信息")
        
        # 检查是否保持了重要信息
        source_numbers = re.findall(r'\d+', source)
        translation_numbers = re.findall(r'\d+', translation)
        
        if source_numbers and not translation_numbers:
            issues.append("翻译中缺少数字信息")
        
        # 检查语言混合问题
        chinese_chars = len(self.chinese_pattern.findall(translation))
        english_chars = len(self.english_pattern.findall(translation))
        
        if chinese_chars > 0 and english_chars > 0:
            chinese_ratio = chinese_chars / len(translation.replace(' ', ''))
            if 0.3 < chinese_ratio < 0.7:
                issues.append("翻译中语言混合过多")
        
        return issues
    
    def _is_english_to_chinese(self, source: str, translation: str) -> bool:
        """判断是否为英译中"""
        source_english = len(self.english_pattern.findall(source))
        source_chinese = len(self.chinese_pattern.findall(source))
        
        translation_english = len(self.english_pattern.findall(translation))
        translation_chinese = len(self.chinese_pattern.findall(translation))
        
        return (source_english > source_chinese and 
                translation_chinese > translation_english)
    
    def _is_chinese_to_english(self, source: str, translation: str) -> bool:
        """判断是否为中译英"""
        source_english = len(self.english_pattern.findall(source))
        source_chinese = len(self.chinese_pattern.findall(source))
        
        translation_english = len(self.english_pattern.findall(translation))
        translation_chinese = len(self.chinese_pattern.findall(translation))
        
        return (source_chinese > source_english and 
                translation_english > translation_chinese)
    
    def _get_confidence_level(self, score: float) -> QualityLevel:
        """根据分数获取置信度等级"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.7:
            return QualityLevel.GOOD
        elif score >= 0.5:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    def get_quality_threshold_recommendation(
        self, 
        text_type: str = "general",
        use_case: str = "draft"
    ) -> float:
        """
        根据文本类型和使用场景推荐质量阈值
        
        Args:
            text_type: 文本类型 ("general", "technical", "literary")
            use_case: 使用场景 ("draft", "review", "final")
            
        Returns:
            float: 推荐的质量阈值
        """
        base_thresholds = {
            "draft": 0.5,
            "review": 0.7,
            "final": 0.8
        }
        
        type_adjustments = {
            "technical": 0.1,   # 技术文档要求更高
            "literary": -0.05,  # 文学作品可以稍微宽松
            "general": 0.0
        }
        
        base_threshold = base_thresholds.get(use_case, 0.7)
        adjustment = type_adjustments.get(text_type, 0.0)
        
        return min(1.0, max(0.0, base_threshold + adjustment))
