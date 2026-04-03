from typing import List, Dict
import random

class QuestionEngine:
    def __init__(self):
        self.question_bank = {
            'college': {
                'tr': [
                    {
                        'id': 'col_tr_1',
                        'question': 'What programming languages are you proficient in?',
                        'type': 'technical',
                        'category': 'programming',
                        'difficulty': 'easy'
                    },
                    {
                        'id': 'col_tr_2',
                        'question': 'Explain the concept of Object-Oriented Programming.',
                        'type': 'technical',
                        'category': 'concepts',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'col_tr_3',
                        'question': 'Write a function to check if a number is prime.',
                        'type': 'coding',
                        'category': 'algorithms',
                        'difficulty': 'easy',
                        'expected_solution': 'def is_prime(n): if n < 2: return False; for i in range(2, int(n**0.5) + 1): if n % i == 0: return False; return True'
                    },
                    {
                        'id': 'col_tr_4',
                        'question': 'What is the difference between SQL and NoSQL databases?',
                        'type': 'technical',
                        'category': 'database',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'col_tr_5',
                        'question': 'Explain the concept of RESTful APIs.',
                        'type': 'technical',
                        'category': 'web',
                        'difficulty': 'medium'
                    }
                ],
                'mr': [
                    {
                        'id': 'col_mr_1',
                        'question': 'How do you handle tight deadlines and pressure?',
                        'type': 'behavioral',
                        'category': 'time_management',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'col_mr_2',
                        'question': 'Describe a situation where you had to work in a team.',
                        'type': 'behavioral',
                        'category': 'teamwork',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'col_mr_3',
                        'question': 'How do you stay updated with the latest technology trends?',
                        'type': 'behavioral',
                        'category': 'learning',
                        'difficulty': 'easy'
                    }
                ],
                'hr': [
                    {
                        'id': 'col_hr_1',
                        'question': 'Tell me about yourself.',
                        'type': 'personal',
                        'category': 'introduction',
                        'difficulty': 'easy'
                    },
                    {
                        'id': 'col_hr_2',
                        'question': 'What are your strengths and weaknesses?',
                        'type': 'personal',
                        'category': 'self_assessment',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'col_hr_3',
                        'question': 'Where do you see yourself in 5 years?',
                        'type': 'personal',
                        'category': 'career_goals',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'col_hr_4',
                        'question': 'Why do you want to join our company?',
                        'type': 'personal',
                        'category': 'motivation',
                        'difficulty': 'medium'
                    }
                ]
            },
            'experienced': {
                'tr': [
                    {
                        'id': 'exp_tr_1',
                        'question': 'Describe a complex technical problem you solved recently.',
                        'type': 'technical',
                        'category': 'problem_solving',
                        'difficulty': 'hard'
                    },
                    {
                        'id': 'exp_tr_2',
                        'question': 'How do you ensure code quality and maintainability?',
                        'type': 'technical',
                        'category': 'best_practices',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'exp_tr_3',
                        'question': 'Design a scalable system for a social media platform.',
                        'type': 'coding',
                        'category': 'system_design',
                        'difficulty': 'hard'
                    },
                    {
                        'id': 'exp_tr_4',
                        'question': 'Explain microservices architecture and its pros/cons.',
                        'type': 'technical',
                        'category': 'architecture',
                        'difficulty': 'hard'
                    }
                ],
                'mr': [
                    {
                        'id': 'exp_mr_1',
                        'question': 'How do you handle conflicts with team members?',
                        'type': 'behavioral',
                        'category': 'conflict_resolution',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'exp_mr_2',
                        'question': 'Describe your leadership style.',
                        'type': 'behavioral',
                        'category': 'leadership',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'exp_mr_3',
                        'question': 'How do you mentor junior developers?',
                        'type': 'behavioral',
                        'category': 'mentoring',
                        'difficulty': 'medium'
                    }
                ],
                'hr': [
                    {
                        'id': 'exp_hr_1',
                        'question': 'Why are you looking for a new opportunity?',
                        'type': 'personal',
                        'category': 'career_change',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'exp_hr_2',
                        'question': 'What are your salary expectations?',
                        'type': 'personal',
                        'category': 'compensation',
                        'difficulty': 'medium'
                    }
                ]
            },
            'ips': {
                'tr': [
                    {
                        'id': 'ips_tr_1',
                        'question': 'What do you know about the Indian Penal Code?',
                        'type': 'technical',
                        'category': 'law',
                        'difficulty': 'hard'
                    },
                    {
                        'id': 'ips_tr_2',
                        'question': 'How would you handle a communal riot situation?',
                        'type': 'situational',
                        'category': 'crisis_management',
                        'difficulty': 'hard'
                    },
                    {
                        'id': 'ips_tr_3',
                        'question': 'Explain the hierarchy of police administration in India.',
                        'type': 'technical',
                        'category': 'administration',
                        'difficulty': 'hard'
                    }
                ],
                'mr': [
                    {
                        'id': 'ips_mr_1',
                        'question': 'How do you maintain integrity in challenging situations?',
                        'type': 'behavioral',
                        'category': 'ethics',
                        'difficulty': 'hard'
                    },
                    {
                        'id': 'ips_mr_2',
                        'question': 'Describe your approach to crowd control.',
                        'type': 'situational',
                        'category': 'law_enforcement',
                        'difficulty': 'hard'
                    }
                ],
                'hr': [
                    {
                        'id': 'ips_hr_1',
                        'question': 'Why do you want to join the police service?',
                        'type': 'personal',
                        'category': 'motivation',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'ips_hr_2',
                        'question': 'What are the qualities of a good police officer?',
                        'type': 'personal',
                        'category': 'self_assessment',
                        'difficulty': 'medium'
                    }
                ]
            },
            'ias': {
                'tr': [
                    {
                        'id': 'ias_tr_1',
                        'question': 'Explain the Indian Constitution and its key features.',
                        'type': 'technical',
                        'category': 'constitution',
                        'difficulty': 'hard'
                    },
                    {
                        'id': 'ias_tr_2',
                        'question': 'What are the major challenges in Indian administration?',
                        'type': 'analytical',
                        'category': 'governance',
                        'difficulty': 'hard'
                    },
                    {
                        'id': 'ias_tr_3',
                        'question': 'Describe the federal structure of India.',
                        'type': 'technical',
                        'category': 'polity',
                        'difficulty': 'hard'
                    }
                ],
                'mr': [
                    {
                        'id': 'ias_mr_1',
                        'question': 'How would you handle a crisis as a district magistrate?',
                        'type': 'situational',
                        'category': 'administration',
                        'difficulty': 'hard'
                    },
                    {
                        'id': 'ias_mr_2',
                        'question': 'What is your approach to implementing government schemes?',
                        'type': 'behavioral',
                        'category': 'implementation',
                        'difficulty': 'hard'
                    }
                ],
                'hr': [
                    {
                        'id': 'ias_hr_1',
                        'question': 'Why do you want to join the civil services?',
                        'type': 'personal',
                        'category': 'motivation',
                        'difficulty': 'medium'
                    },
                    {
                        'id': 'ias_hr_2',
                        'question': 'What role should bureaucracy play in democracy?',
                        'type': 'analytical',
                        'category': 'philosophy',
                        'difficulty': 'hard'
                    }
                ]
            }
        }
    
    def generate_questions(self, interview_type: str, rounds: List[str], level: str) -> List[Dict]:
        questions = []
        
        for round_type in rounds:
            if interview_type in self.question_bank and round_type in self.question_bank[interview_type]:
                round_questions = self.question_bank[interview_type][round_type]
                
                # Select questions based on difficulty level
                if level == 'Entry Level' or level == 'Junior':
                    selected_questions = [q for q in round_questions if q['difficulty'] in ['easy', 'medium']]
                elif level in ['Mid', 'Senior']:
                    selected_questions = [q for q in round_questions if q['difficulty'] in ['medium', 'hard']]
                else:
                    selected_questions = round_questions
                
                # Randomly select 2-3 questions per round
                num_questions = min(3, len(selected_questions))
                chosen_questions = random.sample(selected_questions, num_questions)
                
                for q in chosen_questions:
                    questions.append({
                        **q,
                        'round': round_type,
                        'interview_type': interview_type
                    })
        
        # Shuffle questions
        random.shuffle(questions)
        
        return questions

# Global instance
question_engine = QuestionEngine()

def generate_questions(interview_type: str, rounds: List[str], level: str) -> List[Dict]:
    return question_engine.generate_questions(interview_type, rounds, level)