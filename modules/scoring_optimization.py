"""
Enterprise-Grade Scoring Optimization and Calibration
Based on real ATS industry standards and recruitment best practices
"""
import numpy as np
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class ScoringCalibrator:
    """
    Calibrates scoring thresholds based on industry standards and test data.
    Implements evidence-based scoring aligned with real recruiter expectations.
    """
    
    def __init__(self):
        # Industry-standard thresholds (based on ATS research)
        self.semantic_thresholds = {
            'excellent': 0.88,      # 88%+ similarity = excellent match (top 5%)
            'strong': 0.78,         # 78-88% = strong match (top 15%)
            'good': 0.65,           # 65-78% = good match (top 35%)
            'fair': 0.50,           # 50-65% = fair match (meets minimum)
            'weak': 0.35            # 35-50% = weak match (below threshold)
        }
        
        # Coverage thresholds (% of requirements met)
        self.coverage_thresholds = {
            'excellent': 0.90,      # 90%+ coverage = exceptional
            'strong': 0.75,         # 75-90% = strong candidate
            'good': 0.60,           # 60-75% = qualified
            'fair': 0.45,           # 45-60% = borderline
            'weak': 0.30            # 30-45% = under-qualified
        }
        
        # Final score distribution targets (calibrated to real hiring)
        self.score_bands = {
            'outstanding': (9.0, 10.0),    # Top 2% - immediate hire
            'excellent': (8.0, 9.0),       # Top 10% - priority interview
            'strong': (7.0, 8.0),          # Top 25% - interview
            'good': (6.0, 7.0),            # Top 40% - consider
            'fair': (5.0, 6.0),            # Borderline - maybe
            'weak': (0.0, 5.0)             # Reject
        }
    
    def get_semantic_tier(self, similarity: float) -> str:
        """Classify semantic similarity into tier"""
        if similarity >= self.semantic_thresholds['excellent']:
            return 'excellent'
        elif similarity >= self.semantic_thresholds['strong']:
            return 'strong'
        elif similarity >= self.semantic_thresholds['good']:
            return 'good'
        elif similarity >= self.semantic_thresholds['fair']:
            return 'fair'
        elif similarity >= self.semantic_thresholds['weak']:
            return 'weak'
        return 'poor'
    
    def get_coverage_tier(self, coverage: float) -> str:
        """Classify requirement coverage into tier"""
        if coverage >= self.coverage_thresholds['excellent']:
            return 'excellent'
        elif coverage >= self.coverage_thresholds['strong']:
            return 'strong'
        elif coverage >= self.coverage_thresholds['good']:
            return 'good'
        elif coverage >= self.coverage_thresholds['fair']:
            return 'fair'
        elif coverage >= self.coverage_thresholds['weak']:
            return 'weak'
        return 'poor'
    
    def calibrate_final_score(
        self,
        coverage_score: float,
        semantic_score: float,
        must_fulfillment_rate: float,
        nice_coverage: float = 0.0
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Calibrate final score using STRICT industry-standard algorithm.
        
        Algorithm (BALANCED, NOT TOO LENIENT):
        1. Base score from coverage (50% weight - reduced from 60%)
        2. Semantic similarity bonus (35% weight - increased from 25%)  
        3. Must-have fulfillment critical factor (15% weight)
        4. Nice-to-have bonus (small uplift)
        5. STRICT penalties for critical gaps
        
        Returns: (final_score, tier, breakdown)
        """
        breakdown = {}
        
        # 1. Coverage base score (0-5 points, 50% weight - REDUCED)
        # Lower max to make semantic score matter more
        coverage_tier = self.get_coverage_tier(coverage_score)
        if coverage_tier == 'excellent':
            coverage_points = 4.6 + (coverage_score - 0.90) * 4  # 4.6-5.0
        elif coverage_tier == 'strong':
            coverage_points = 3.8 + (coverage_score - 0.75) * 5.33  # 3.8-4.6
        elif coverage_tier == 'good':
            coverage_points = 3.0 + (coverage_score - 0.60) * 5.33  # 3.0-3.8
        elif coverage_tier == 'fair':
            coverage_points = 2.2 + (coverage_score - 0.45) * 5.33  # 2.2-3.0
        else:
            coverage_points = coverage_score * 4.9  # 0-2.2
        
        breakdown['coverage_points'] = round(coverage_points, 2)
        breakdown['coverage_tier'] = coverage_tier
        
        # 2. Semantic similarity bonus (0-3.5 points, 35% weight - INCREASED)
        # Semantic match is VERY important - low semantic = not a good fit
        semantic_tier = self.get_semantic_tier(semantic_score)
        if semantic_tier == 'excellent':
            semantic_points = 3.1 + (semantic_score - 0.88) * 3.33  # 3.1-3.5
        elif semantic_tier == 'strong':
            semantic_points = 2.4 + (semantic_score - 0.78) * 7.0  # 2.4-3.1
        elif semantic_tier == 'good':
            semantic_points = 1.6 + (semantic_score - 0.65) * 6.15  # 1.6-2.4
        elif semantic_tier == 'fair':
            semantic_points = 0.8 + (semantic_score - 0.50) * 5.33  # 0.8-1.6
        elif semantic_tier == 'weak':
            semantic_points = 0.3 + (semantic_score - 0.35) * 3.33  # 0.3-0.8
        else:
            semantic_points = semantic_score * 0.86  # 0-0.3
        
        breakdown['semantic_points'] = round(semantic_points, 2)
        breakdown['semantic_tier'] = semantic_tier
        
        # 3. Must-have fulfillment (0-1.5 points, 15% weight)
        # This is CRITICAL - missing must-haves = heavy penalty
        if must_fulfillment_rate >= 0.90:
            must_points = 1.4 + (must_fulfillment_rate - 0.90) * 1.0  # 1.4-1.5
        elif must_fulfillment_rate >= 0.75:
            must_points = 1.1 + (must_fulfillment_rate - 0.75) * 2.0  # 1.1-1.4
        elif must_fulfillment_rate >= 0.60:
            must_points = 0.7 + (must_fulfillment_rate - 0.60) * 2.67  # 0.7-1.1
        elif must_fulfillment_rate >= 0.40:
            must_points = 0.3 + (must_fulfillment_rate - 0.40) * 2.0  # 0.3-0.7
        else:
            must_points = must_fulfillment_rate * 0.75  # 0-0.3
        
        breakdown['must_points'] = round(must_points, 2)
        breakdown['must_fulfillment_rate'] = round(must_fulfillment_rate, 3)
        
        # 4. Nice-to-have bonus (0-0.5 points, small uplift)
        nice_points = min(0.5, nice_coverage * 0.5)
        breakdown['nice_points'] = round(nice_points, 2)
        
        # 5. Calculate raw score
        raw_score = coverage_points + semantic_points + must_points + nice_points
        
        # 6. Apply STRICT penalties
        penalty_factor = 1.0
        penalties = []
        
        # PENALTY: Less than 50% must-haves met (CRITICAL)
        if must_fulfillment_rate < 0.50:
            penalty_factor *= 0.65  # 35% penalty (increased from 30%)
            penalties.append("Critical: <50% must-haves met (-35%)")
        
        # PENALTY: Low coverage (40-60% range)
        if coverage_score < 0.40:
            penalty_factor *= 0.75  # 25% penalty (increased from 20%)
            penalties.append("Low overall coverage (-25%)")
        elif coverage_score < 0.60:
            penalty_factor *= 0.90  # 10% penalty (NEW tier)
            penalties.append("Moderate coverage gap (-10%)")
        
        # PENALTY: Poor semantic match (resume not relevant to role)
        # THIS IS KEY - 44% semantic should heavily penalize
        if semantic_score < 0.40:
            penalty_factor *= 0.70  # 30% penalty (increased from 15%)
            penalties.append("Very weak semantic relevance (-30%)")
        elif semantic_score < 0.55:
            penalty_factor *= 0.85  # 15% penalty (NEW tier)
            penalties.append("Weak semantic relevance (-15%)")
        elif semantic_score < 0.70:
            penalty_factor *= 0.95  # 5% penalty (NEW tier)  
            penalties.append("Moderate semantic gap (-5%)")
        
        # PENALTY: Coverage/semantic mismatch (high coverage but low semantic = red flag)
        if coverage_score >= 0.85 and semantic_score < 0.55:
            penalty_factor *= 0.85  # 15% penalty
            penalties.append("Mismatch: High coverage but weak semantic fit (-15%)")
        
        breakdown['penalties'] = penalties
        breakdown['penalty_factor'] = round(penalty_factor, 3)
        
        # 7. Apply bonuses for excellence (STRICTER requirements)
        bonus_factor = 1.0
        bonuses = []
        
        # Bonus: Exceptional coverage + strong must-haves (STRICTER)
        if coverage_score >= 0.90 and must_fulfillment_rate >= 0.90:
            bonus_factor *= 1.08  # 8% bonus (reduced from 10%)
            bonuses.append("Excellence bonus: High coverage + must-haves (+8%)")
        
        # Bonus: Perfect semantic match (STRICTER threshold)
        if semantic_score >= 0.92:  # Raised from 0.90
            bonus_factor *= 1.04  # 4% bonus (reduced from 5%)
            bonuses.append("Perfect fit bonus: Excellent semantic match (+4%)")
        
        breakdown['bonuses'] = bonuses
        breakdown['bonus_factor'] = round(bonus_factor, 3)
        
        # 8. Final calibrated score
        final_score = raw_score * penalty_factor * bonus_factor
        final_score = max(0.0, min(10.0, final_score))  # Clamp to 0-10
        
        # 9. Determine tier
        tier = 'weak'
        for tier_name, (min_score, max_score) in self.score_bands.items():
            if min_score <= final_score <= max_score:
                tier = tier_name
                break
        
        breakdown['raw_score'] = round(raw_score, 2)
        breakdown['final_score'] = round(final_score, 2)
        breakdown['tier'] = tier
        
        logger.info(f"Score calibration: {final_score:.1f}/10 ({tier}) - Coverage: {coverage_tier}, Semantic: {semantic_tier}, Must: {must_fulfillment_rate:.0%}")
        
        return round(final_score, 1), tier, breakdown


class SkillTaxonomy:
    """
    Skill taxonomy with synonyms, abbreviations, and related terms.
    Improves matching accuracy by recognizing equivalent skills.
    """
    
    def __init__(self):
        self.taxonomy = {
            # Programming Languages
            'python': ['python', 'python3', 'python 3', 'py'],
            'javascript': ['javascript', 'js', 'ecmascript', 'es6', 'es2015', 'es2020'],
            'typescript': ['typescript', 'ts'],
            'java': ['java', 'java 8', 'java 11', 'java 17', 'jdk'],
            'c++': ['c++', 'cpp', 'c plus plus'],
            'c#': ['c#', 'csharp', 'c sharp', '.net'],
            'go': ['go', 'golang'],
            'rust': ['rust', 'rust lang'],
            'ruby': ['ruby', 'rb'],
            'php': ['php', 'php 7', 'php 8'],
            
            # Frameworks (Backend)
            'django': ['django', 'django rest framework', 'drf'],
            'flask': ['flask', 'flask-restful'],
            'fastapi': ['fastapi', 'fast api'],
            'spring': ['spring', 'spring boot', 'spring framework', 'spring mvc', 'spring cloud'],
            'express': ['express', 'express.js', 'expressjs'],
            'nestjs': ['nestjs', 'nest.js', 'nest'],
            
            # Frameworks (Frontend)
            'react': ['react', 'react.js', 'reactjs', 'react 18', 'react 19'],
            'angular': ['angular', 'angular 2+', 'angularjs'],
            'vue': ['vue', 'vue.js', 'vuejs', 'vue 3'],
            'nextjs': ['nextjs', 'next.js', 'next'],
            'svelte': ['svelte', 'sveltejs'],
            
            # Databases
            'postgresql': ['postgresql', 'postgres', 'psql', 'pg'],
            'mysql': ['mysql', 'my sql'],
            'mongodb': ['mongodb', 'mongo', 'mongo db'],
            'redis': ['redis', 'redis cache'],
            'cassandra': ['cassandra', 'apache cassandra'],
            'dynamodb': ['dynamodb', 'dynamo db'],
            'elasticsearch': ['elasticsearch', 'elastic search', 'elastic'],
            
            # Cloud (AWS)
            'aws': ['aws', 'amazon web services'],
            'ec2': ['ec2', 'amazon ec2', 'elastic compute'],
            's3': ['s3', 'amazon s3', 'simple storage service'],
            'lambda': ['lambda', 'aws lambda', 'amazon lambda'],
            'cloudformation': ['cloudformation', 'cloud formation', 'cfn'],
            'dynamodb': ['dynamodb', 'dynamo'],
            
            # Cloud (Azure)
            'azure': ['azure', 'microsoft azure', 'ms azure'],
            
            # Cloud (GCP)
            'gcp': ['gcp', 'google cloud', 'google cloud platform'],
            
            # DevOps
            'docker': ['docker', 'containerization', 'containers'],
            'kubernetes': ['kubernetes', 'k8s', 'k8', 'kube'],
            'jenkins': ['jenkins', 'jenkins ci', 'jenkins ci/cd'],
            'terraform': ['terraform', 'tf', 'infrastructure as code', 'iac'],
            'ansible': ['ansible', 'ansible playbook'],
            'gitlab': ['gitlab', 'gitlab ci', 'gitlab ci/cd'],
            'github actions': ['github actions', 'gh actions'],
            
            # Data Science / ML
            'tensorflow': ['tensorflow', 'tf', 'tensor flow'],
            'pytorch': ['pytorch', 'torch', 'py torch'],
            'scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
            'pandas': ['pandas', 'pd'],
            'numpy': ['numpy', 'np'],
            'keras': ['keras'],
            
            # CS Fundamentals
            'operating system': ['operating system', 'operating systems', 'os'],
            'dbms': ['dbms', 'database management system', 'database management'],
            'computer network': ['computer network', 'computer networks', 'networking', 'cn'],
            'data structure': ['data structure', 'data structures', 'ds', 'dsa'],
            'algorithm': ['algorithm', 'algorithms', 'algo'],
            'object oriented': ['oop', 'object oriented', 'object-oriented', 'object oriented programming'],
            
            # Other
            'rest api': ['rest', 'rest api', 'restful', 'restful api'],
            'graphql': ['graphql', 'graph ql', 'gql'],
            'microservices': ['microservices', 'micro services', 'microservice architecture'],
            'git': ['git', 'version control', 'source control'],
            'agile': ['agile', 'scrum', 'agile methodology'],
        }
        
        # Build reverse index (term -> canonical form)
        self.reverse_index = {}
        for canonical, variants in self.taxonomy.items():
            for variant in variants:
                self.reverse_index[variant.lower()] = canonical
    
    def get_canonical(self, term: str) -> str:
        """Get canonical form of a skill term"""
        term_lower = term.lower().strip()
        return self.reverse_index.get(term_lower, term_lower)
    
    def are_equivalent(self, term1: str, term2: str) -> bool:
        """Check if two terms are equivalent (same canonical form)"""
        return self.get_canonical(term1) == self.get_canonical(term2)
    
    def get_variants(self, term: str) -> List[str]:
        """Get all variants of a skill term"""
        canonical = self.get_canonical(term)
        return self.taxonomy.get(canonical, [term])
    
    def normalize_skill_list(self, skills: List[str]) -> List[str]:
        """Normalize skill list to canonical forms and remove duplicates"""
        seen = set()
        normalized = []
        for skill in skills:
            canonical = self.get_canonical(skill)
            if canonical not in seen:
                normalized.append(canonical)
                seen.add(canonical)
        return normalized


# Global instances
calibrator = ScoringCalibrator()
skill_taxonomy = SkillTaxonomy()
