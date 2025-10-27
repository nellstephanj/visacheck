"""Decision Agent Service - AI-powered visa application decision recommendation system"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DecisionAgentService:
    """Service for generating visa application decision recommendations"""
    
    def __init__(self, azure_handler, openai_handler):
        self.azure_handler = azure_handler
        self.openai_handler = openai_handler
        
    def calculate_funds_score(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate funds sufficiency score (max 40 points)
        
        Args:
            application_data: Application data including bank statements
            
        Returns:
            Dictionary with score and reasoning
        """
        try:
            # Extract financial data
            bank_balance = float(application_data.get('bank_balance', 0))
            duration_days = int(application_data.get('duration_days', 30))
            accommodation_cost = float(application_data.get('accommodation_cost', 0))
            
            # Define daily rate thresholds (configurable by destination)
            destination = application_data.get('destination_country', 'Germany')
            daily_rates = {
                'Germany': 80,
                'France': 90,
                'Italy': 75,
                'Spain': 70,
                'Netherlands': 85,
                'default': 80
            }
            
            daily_rate = daily_rates.get(destination, daily_rates['default'])
            
            # Calculate required funds
            buffer_percentage = 0.20  # 20% safety buffer
            required_daily_funds = daily_rate * duration_days
            total_required = required_daily_funds + accommodation_cost
            total_with_buffer = total_required * (1 + buffer_percentage)
            
            # Calculate coverage percentage
            coverage_percentage = (bank_balance / total_with_buffer) * 100 if total_with_buffer > 0 else 0
            
            # Score calculation (max 40 points)
            if coverage_percentage >= 120:
                score = 40
                reason = f"Excellent funds: Balance covers {coverage_percentage:.1f}% of requirements with buffer."
            elif coverage_percentage >= 100:
                score = 35
                reason = f"Adequate funds: Balance covers {coverage_percentage:.1f}% of requirements."
            elif coverage_percentage >= 85:
                score = 30
                reason = f"Marginal funds: Balance covers {coverage_percentage:.1f}% of requirements (85%+ threshold)."
            elif coverage_percentage >= 70:
                score = 20
                reason = f"Insufficient funds: Balance only covers {coverage_percentage:.1f}% of requirements."
            else:
                score = 10
                reason = f"Severely insufficient funds: Balance covers only {coverage_percentage:.1f}% of requirements."
            
            # Check for suspicious large inflows
            recent_inflow = application_data.get('recent_large_inflow', False)
            inflow_days_ago = application_data.get('inflow_days_ago', 0)
            
            flags = []
            if recent_inflow and inflow_days_ago <= 14:
                score = max(0, score - 10)
                flags.append(f"Large deposit detected {inflow_days_ago} days ago - may require explanation")
            
            return {
                'score': score,
                'max_score': 40,
                'reason': reason,
                'details': {
                    'bank_balance': bank_balance,
                    'required_funds': total_required,
                    'required_with_buffer': total_with_buffer,
                    'coverage_percentage': round(coverage_percentage, 2),
                    'daily_rate': daily_rate,
                    'duration_days': duration_days
                },
                'flags': flags
            }
            
        except Exception as e:
            logger.error(f"Error calculating funds score: {str(e)}")
            return {
                'score': 0,
                'max_score': 40,
                'reason': f"Error calculating funds score: {str(e)}",
                'details': {},
                'flags': ['Unable to verify financial sufficiency']
            }
    
    def calculate_travel_proof_score(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate travel proof completeness score (max 20 points)
        
        Args:
            application_data: Application data including flight and hotel info
            
        Returns:
            Dictionary with score and reasoning
        """
        try:
            score = 0
            max_score = 20
            flags = []
            
            # Flight ticket check (10 points)
            has_return_flight = application_data.get('has_return_flight', False)
            flight_dates_consistent = application_data.get('flight_dates_consistent', False)
            flight_names_match = application_data.get('flight_names_match', True)
            
            if has_return_flight and flight_dates_consistent and flight_names_match:
                score += 10
                flight_reason = "Round-trip booking confirmed with consistent dates and names."
            elif has_return_flight and flight_dates_consistent:
                score += 8
                flight_reason = "Round-trip booking confirmed but minor name discrepancies."
                flags.append("Minor name mismatch between flight ticket and passport")
            elif has_return_flight:
                score += 5
                flight_reason = "Return flight exists but dates inconsistent with itinerary."
                flags.append("Flight dates do not align with stated travel plan")
            else:
                flight_reason = "No return flight booking found."
                flags.append("Missing return flight confirmation")
            
            # Hotel reservation check (10 points)
            hotel_coverage = float(application_data.get('hotel_coverage_percentage', 0))
            hotel_refundable = application_data.get('hotel_refundable', False)
            duration_days = int(application_data.get('duration_days', 30))
            
            if hotel_coverage >= 95:
                score += 10
                hotel_reason = f"Hotel coverage: {hotel_coverage:.0f}% of stay confirmed."
            elif hotel_coverage >= 80:
                score += 8
                hotel_reason = f"Hotel coverage: {hotel_coverage:.0f}% of stay (minor gaps acceptable)."
            elif hotel_coverage >= 60:
                score += 5
                hotel_reason = f"Partial hotel coverage: {hotel_coverage:.0f}% of stay."
                flags.append(f"Hotel reservations cover only {hotel_coverage:.0f}% of travel duration")
            else:
                score += 2
                hotel_reason = f"Inadequate hotel coverage: {hotel_coverage:.0f}% of stay."
                flags.append(f"Insufficient accommodation proof - only {hotel_coverage:.0f}% coverage")
            
            # Refundable booking warning
            if not hotel_refundable and hotel_coverage > 0:
                flags.append("Hotel bookings are refundable - lower commitment level")
            
            combined_reason = f"{flight_reason} {hotel_reason}"
            
            return {
                'score': score,
                'max_score': max_score,
                'reason': combined_reason,
                'details': {
                    'has_return_flight': has_return_flight,
                    'flight_dates_consistent': flight_dates_consistent,
                    'flight_names_match': flight_names_match,
                    'hotel_coverage_percentage': hotel_coverage,
                    'hotel_refundable': hotel_refundable
                },
                'flags': flags
            }
            
        except Exception as e:
            logger.error(f"Error calculating travel proof score: {str(e)}")
            return {
                'score': 0,
                'max_score': 20,
                'reason': f"Error calculating travel proof score: {str(e)}",
                'details': {},
                'flags': ['Unable to verify travel documentation']
            }
    
    def calculate_background_score(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate background check score (max 20 points)
        
        Args:
            application_data: Application data including police report and watchlist status
            
        Returns:
            Dictionary with score and reasoning
        """
        try:
            score = 0
            max_score = 20
            flags = []
            
            # Police report check (10 points)
            police_report_status = application_data.get('police_report_status', 'missing')
            
            if police_report_status == 'clear':
                score += 10
                police_reason = "Police report clear - no criminal records."
            elif police_report_status == 'issues':
                score += 3
                police_reason = "Police report shows issues - requires review."
                flags.append("Police report indicates criminal history or concerns")
            else:
                score += 0
                police_reason = "Police report missing or invalid."
                flags.append("Missing or incomplete police clearance certificate")
            
            # Schengen watchlist check (10 points)
            watchlist_status = application_data.get('watchlist_status', 'unknown')
            prior_violations = application_data.get('prior_violations', False)
            entry_ban = application_data.get('entry_ban', False)
            
            if entry_ban:
                score += 0
                watchlist_reason = "Active entry ban in Schengen database."
                flags.append("CRITICAL: Active Schengen entry ban detected")
            elif prior_violations:
                score += 3
                watchlist_reason = "Prior Schengen violations recorded."
                flags.append("Previous Schengen visa violations found")
            elif watchlist_status == 'clear':
                score += 10
                watchlist_reason = "No negative hits in Schengen partner databases."
            else:
                score += 7
                watchlist_reason = "Watchlist check inconclusive - no alerts found."
            
            combined_reason = f"{police_reason} {watchlist_reason}"
            
            return {
                'score': score,
                'max_score': max_score,
                'reason': combined_reason,
                'details': {
                    'police_report_status': police_report_status,
                    'watchlist_status': watchlist_status,
                    'prior_violations': prior_violations,
                    'entry_ban': entry_ban
                },
                'flags': flags
            }
            
        except Exception as e:
            logger.error(f"Error calculating background score: {str(e)}")
            return {
                'score': 0,
                'max_score': 20,
                'reason': f"Error calculating background score: {str(e)}",
                'details': {},
                'flags': ['Unable to complete background verification']
            }
    
    def calculate_consistency_score(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate consistency and authenticity score (max 20 points)
        
        Args:
            application_data: Application data for cross-document verification
            
        Returns:
            Dictionary with score and reasoning
        """
        try:
            score = 20  # Start with perfect score
            max_score = 20
            flags = []
            
            # Name consistency check
            name_consistent = application_data.get('name_consistent_across_documents', True)
            if not name_consistent:
                score -= 5
                flags.append("Name inconsistencies detected across documents")
            
            # Date consistency check
            dates_consistent = application_data.get('dates_consistent', True)
            if not dates_consistent:
                score -= 5
                flags.append("Date discrepancies found in submitted documents")
            
            # MRZ validation
            mrz_valid = application_data.get('mrz_valid', True)
            if not mrz_valid:
                score -= 7
                flags.append("Passport MRZ validation failed - possible authenticity issue")
            
            # Document integrity
            document_integrity = application_data.get('document_integrity_score', 100)
            if document_integrity < 90:
                score -= 3
                flags.append(f"Document integrity concerns (score: {document_integrity}%)")
            
            # Photo consistency
            photo_match = application_data.get('photo_match_confidence', 100)
            if photo_match < 85:
                score -= 5
                flags.append(f"Low photo match confidence ({photo_match}%) across documents")
            
            score = max(0, score)  # Ensure non-negative
            
            if score >= 18:
                reason = "Excellent consistency across all documents."
            elif score >= 15:
                reason = "Good consistency with minor discrepancies."
            elif score >= 10:
                reason = "Moderate consistency issues requiring attention."
            else:
                reason = "Significant consistency and authenticity concerns."
            
            return {
                'score': score,
                'max_score': max_score,
                'reason': reason,
                'details': {
                    'name_consistent': name_consistent,
                    'dates_consistent': dates_consistent,
                    'mrz_valid': mrz_valid,
                    'document_integrity_score': document_integrity,
                    'photo_match_confidence': photo_match
                },
                'flags': flags
            }
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {str(e)}")
            return {
                'score': 0,
                'max_score': 20,
                'reason': f"Error calculating consistency score: {str(e)}",
                'details': {},
                'flags': ['Unable to verify document consistency']
            }
    
    def generate_decision_recommendation(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive decision recommendation
        
        Args:
            application_data: Complete application data with verification results
            
        Returns:
            Decision recommendation with score breakdown and reasoning
        """
        try:
            # Calculate all scores
            funds_result = self.calculate_funds_score(application_data)
            travel_result = self.calculate_travel_proof_score(application_data)
            background_result = self.calculate_background_score(application_data)
            consistency_result = self.calculate_consistency_score(application_data)
            
            # Calculate total score
            total_score = (
                funds_result['score'] +
                travel_result['score'] +
                background_result['score'] +
                consistency_result['score']
            )
            
            # Collect all flags
            blocking_issues = []
            soft_concerns = []
            
            all_flags = (
                funds_result.get('flags', []) +
                travel_result.get('flags', []) +
                background_result.get('flags', []) +
                consistency_result.get('flags', [])
            )
            
            # Categorize flags
            for flag in all_flags:
                if any(keyword in flag.upper() for keyword in ['CRITICAL', 'ENTRY BAN', 'MRZ VALIDATION FAILED']):
                    blocking_issues.append(flag)
                else:
                    soft_concerns.append(flag)
            
            # Determine recommendation status
            if blocking_issues:
                status = "MANUAL_REVIEW"
                justification = "Application requires manual review due to critical blocking issues."
            elif total_score >= 85:
                status = "APPROVE"
                justification = "Application meets all requirements with high confidence. Recommended for approval."
            elif total_score >= 60:
                status = "MANUAL_REVIEW"
                justification = "Application shows moderate concerns. Manual review recommended to assess risk factors."
            else:
                status = "REJECT"
                justification = "Application fails to meet minimum requirements. Recommended for rejection."
            
            # Generate policy references
            policy_refs = []
            if funds_result['score'] < 30:
                policy_refs.append("POL-FUNDS-1.3")
            if travel_result['score'] < 15:
                policy_refs.append("POL-TRAVEL-2.0")
            if background_result['score'] < 15:
                policy_refs.append("POL-SEC-1.1")
            if consistency_result['score'] < 15:
                policy_refs.append("POL-AUTH-3.2")
            
            # Build comprehensive recommendation
            recommendation = {
                'decision_recommendation': {
                    'status': status,
                    'score': total_score,
                    'score_breakdown': {
                        'funds': {
                            'score': funds_result['score'],
                            'max_score': funds_result['max_score'],
                            'reason': funds_result['reason'],
                            'details': funds_result['details']
                        },
                        'travel_proof': {
                            'score': travel_result['score'],
                            'max_score': travel_result['max_score'],
                            'reason': travel_result['reason'],
                            'details': travel_result['details']
                        },
                        'background': {
                            'score': background_result['score'],
                            'max_score': background_result['max_score'],
                            'reason': background_result['reason'],
                            'details': background_result['details']
                        },
                        'consistency': {
                            'score': consistency_result['score'],
                            'max_score': consistency_result['max_score'],
                            'reason': consistency_result['reason'],
                            'details': consistency_result['details']
                        }
                    },
                    'blocking_issues': blocking_issues,
                    'soft_concerns': soft_concerns,
                    'policy_refs': policy_refs,
                    'justification': justification,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating decision recommendation: {str(e)}")
            return {
                'decision_recommendation': {
                    'status': 'ERROR',
                    'score': 0,
                    'score_breakdown': {},
                    'blocking_issues': [f'Error generating recommendation: {str(e)}'],
                    'soft_concerns': [],
                    'policy_refs': [],
                    'justification': 'Unable to generate recommendation due to system error.',
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
    
    async def get_ai_recommendation_explanation(self, recommendation: Dict[str, Any], application_data: Dict[str, Any]) -> str:
        """
        Use OpenAI to generate a human-readable explanation of the recommendation
        
        Args:
            recommendation: The decision recommendation data
            application_data: Original application data
            
        Returns:
            Human-readable explanation string
        """
        try:
            decision = recommendation['decision_recommendation']
            
            prompt = f"""You are a senior visa officer providing expert analysis of a visa application decision recommendation.

Application Overview:
- Application Number: {application_data.get('application_number', 'N/A')}
- Applicant: {application_data.get('given_name', '')} {application_data.get('surname', '')}
- Nationality: {application_data.get('country_of_nationality', 'N/A')}
- Visa Type: {application_data.get('visa_type_requested', 'N/A')}

AI Recommendation: {decision['status']}
Overall Score: {decision['score']}/100

Score Breakdown:
- Funds Sufficiency: {decision['score_breakdown']['funds']['score']}/{decision['score_breakdown']['funds']['max_score']} - {decision['score_breakdown']['funds']['reason']}
- Travel Proof: {decision['score_breakdown']['travel_proof']['score']}/{decision['score_breakdown']['travel_proof']['max_score']} - {decision['score_breakdown']['travel_proof']['reason']}
- Background Check: {decision['score_breakdown']['background']['score']}/{decision['score_breakdown']['background']['max_score']} - {decision['score_breakdown']['background']['reason']}
- Document Consistency: {decision['score_breakdown']['consistency']['score']}/{decision['score_breakdown']['consistency']['max_score']} - {decision['score_breakdown']['consistency']['reason']}

Blocking Issues: {', '.join(decision['blocking_issues']) if decision['blocking_issues'] else 'None'}
Soft Concerns: {', '.join(decision['soft_concerns']) if decision['soft_concerns'] else 'None'}

Provide a comprehensive, professional analysis in 3-4 paragraphs that:
1. Summarizes the key strengths and weaknesses of the application
2. Explains the rationale behind the AI recommendation
3. Highlights critical issues that require human judgment
4. Provides guidance on what aspects the human officer should focus on

Write in a professional tone suitable for government case officers."""

            messages = [
                {"role": "system", "content": "You are an expert visa application analyst providing decision support to human officers."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.openai_handler.client.chat.completions.create(
                model=self.openai_handler.model_name_gpt,
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI explanation: {str(e)}")
            return "Unable to generate AI explanation at this time."
