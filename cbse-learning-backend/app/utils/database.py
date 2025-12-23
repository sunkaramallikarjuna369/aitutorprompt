from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from ..models.user import User, LearningStyle
from ..models.curriculum import Class, Subject, Chapter, Topic, LearningObjective, ContentBlock
from ..models.quiz import Question, QuizSession, QuizAttempt, Quiz, BloomLevel, QuestionType, QuestionOption
from ..models.progress import Progress, ProgressStatus, TopicProgress
from ..models.rwal import RealWorldScenario, PersonalizedExample

class InMemoryDatabase:
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.user_passwords: Dict[str, str] = {}
        self.classes: Dict[str, Dict] = {}
        self.subjects: Dict[str, Dict] = {}
        self.chapters: Dict[str, Dict] = {}
        self.topics: Dict[str, Dict] = {}
        self.questions: Dict[str, Dict] = {}
        self.quiz_sessions: Dict[str, Dict] = {}
        self.quiz_attempts: Dict[str, Dict] = {}
        self.quizzes: Dict[str, Dict] = {}
        self.progress: Dict[str, Dict] = {}
        self.rwal_scenarios: Dict[str, Dict] = {}
        self.personalized_examples: Dict[str, Dict] = {}
        self.visual_configs: Dict[str, Dict] = {}
        self._seed_data()
    
    def _seed_data(self):
        self._seed_curriculum()
        self._seed_questions()
        self._seed_rwal_scenarios()
        self._seed_visual_configs()
    
    def _seed_curriculum(self):
        class_10 = {
            "id": "class-10",
            "board": "CBSE",
            "grade": 10,
            "name": "Class 10",
            "description": "CBSE Class 10 curriculum covering all core subjects",
            "subjects": ["maths-10"]
        }
        self.classes["class-10"] = class_10
        
        maths = {
            "id": "maths-10",
            "class_id": "class-10",
            "name": "Mathematics",
            "code": "MATHS",
            "description": "CBSE Class 10 Mathematics covering Algebra, Geometry, Trigonometry, and Statistics",
            "chapters": ["quadratic-equations"],
            "icon": "calculator"
        }
        self.subjects["maths-10"] = maths
        
        quadratic_chapter = {
            "id": "quadratic-equations",
            "subject_id": "maths-10",
            "name": "Quadratic Equations",
            "number": 4,
            "description": "Learn about quadratic equations, their solutions, and real-world applications. Master factorization, completing the square, and the quadratic formula.",
            "difficulty": "medium",
            "topics": ["qe-intro", "qe-standard-form", "qe-factorization", "qe-completing-square", "qe-quadratic-formula", "qe-nature-of-roots", "qe-applications"],
            "learning_objectives": [
                "Understand the standard form of quadratic equations",
                "Solve quadratic equations using factorization",
                "Apply the method of completing the square",
                "Use the quadratic formula to find roots",
                "Determine the nature of roots using discriminant",
                "Apply quadratic equations to real-world problems"
            ],
            "prerequisites": ["linear-equations", "algebraic-expressions"],
            "estimated_time_hours": 3.0
        }
        self.chapters["quadratic-equations"] = quadratic_chapter
        
        topics_data = [
            {
                "id": "qe-intro",
                "chapter_id": "quadratic-equations",
                "name": "Introduction to Quadratic Equations",
                "description": "Discover what quadratic equations are and where they appear in the real world",
                "order": 1,
                "learning_objectives": [
                    {"id": "lo-1", "description": "Identify quadratic equations from given expressions", "bloom_level": "remember", "keywords": ["identify", "recognize"]},
                    {"id": "lo-2", "description": "Understand the relationship between quadratic equations and parabolas", "bloom_level": "understand", "keywords": ["explain", "describe"]}
                ],
                "content_blocks": [
                    {"id": "cb-intro-1", "type": "scenario", "title": "The Bridge Builder's Challenge", "content": "Imagine you're an engineer designing a beautiful arch bridge. The curve of the arch follows a special mathematical shape called a parabola. To design this perfectly, you need to understand quadratic equations!", "order": 1, "metadata": {"sgt_entry": True}},
                    {"id": "cb-intro-2", "type": "text", "title": "What is a Quadratic Equation?", "content": "A quadratic equation is a polynomial equation of degree 2. It contains a variable raised to the power of 2 (squared) as its highest power. The word 'quadratic' comes from 'quad' meaning square.", "order": 2, "metadata": {}},
                    {"id": "cb-intro-3", "type": "definition", "title": "Standard Form", "content": "The standard form of a quadratic equation is: ax² + bx + c = 0, where a, b, and c are constants (real numbers), and a ≠ 0. Here, x is the variable we want to solve for.", "order": 3, "metadata": {"formula": "ax² + bx + c = 0"}},
                    {"id": "cb-intro-4", "type": "example", "title": "Examples of Quadratic Equations", "content": "1. x² - 5x + 6 = 0 (a=1, b=-5, c=6)\n2. 2x² + 3x - 2 = 0 (a=2, b=3, c=-2)\n3. x² - 4 = 0 (a=1, b=0, c=-4)\n4. 3x² + 7x = 0 (a=3, b=7, c=0)", "order": 4, "metadata": {}}
                ],
                "rwal_refs": ["rwal-bridge", "rwal-projectile"],
                "visual_config_refs": ["vis-parabola-intro"],
                "tags": ["introduction", "basics", "visual"],
                "estimated_time_minutes": 15
            },
            {
                "id": "qe-standard-form",
                "chapter_id": "quadratic-equations",
                "name": "Standard Form and Coefficients",
                "description": "Master the standard form ax² + bx + c = 0 and understand the role of each coefficient",
                "order": 2,
                "learning_objectives": [
                    {"id": "lo-3", "description": "Convert equations to standard form", "bloom_level": "apply", "keywords": ["convert", "transform"]},
                    {"id": "lo-4", "description": "Identify coefficients a, b, and c", "bloom_level": "remember", "keywords": ["identify", "extract"]}
                ],
                "content_blocks": [
                    {"id": "cb-sf-1", "type": "text", "title": "Understanding Coefficients", "content": "In the equation ax² + bx + c = 0:\n• 'a' is the coefficient of x² (leading coefficient)\n• 'b' is the coefficient of x\n• 'c' is the constant term\n\nThe value of 'a' determines whether the parabola opens upward (a > 0) or downward (a < 0).", "order": 1, "metadata": {}},
                    {"id": "cb-sf-2", "type": "interactive", "title": "Coefficient Explorer", "content": "Use the sliders to change the values of a, b, and c. Watch how the parabola changes shape!", "order": 2, "metadata": {"visual_type": "parabola_explorer"}, "visual_config_ref": "vis-coefficient-explorer"},
                    {"id": "cb-sf-3", "type": "worked_example", "title": "Converting to Standard Form", "content": "Convert 3x² = 5x - 2 to standard form:\n\nStep 1: Move all terms to one side\n3x² - 5x + 2 = 0\n\nStep 2: Identify coefficients\na = 3, b = -5, c = 2", "order": 3, "metadata": {"steps": ["Move all terms to left side", "Arrange in descending powers of x", "Identify a, b, c"]}}
                ],
                "rwal_refs": [],
                "visual_config_refs": ["vis-coefficient-explorer"],
                "tags": ["standard-form", "coefficients", "interactive"],
                "estimated_time_minutes": 20
            },
            {
                "id": "qe-factorization",
                "chapter_id": "quadratic-equations",
                "name": "Solving by Factorization",
                "description": "Learn to solve quadratic equations by splitting the middle term and factoring",
                "order": 3,
                "learning_objectives": [
                    {"id": "lo-5", "description": "Factor quadratic expressions", "bloom_level": "apply", "keywords": ["factor", "split"]},
                    {"id": "lo-6", "description": "Solve equations using zero product property", "bloom_level": "apply", "keywords": ["solve", "find roots"]}
                ],
                "content_blocks": [
                    {"id": "cb-fact-1", "type": "text", "title": "The Factorization Method", "content": "Factorization works by expressing the quadratic as a product of two linear factors. If (x - p)(x - q) = 0, then either x - p = 0 or x - q = 0, giving us x = p or x = q.", "order": 1, "metadata": {}},
                    {"id": "cb-fact-2", "type": "method", "title": "Splitting the Middle Term", "content": "To factor ax² + bx + c:\n1. Find two numbers whose product is ac and sum is b\n2. Split bx using these numbers\n3. Factor by grouping\n4. Apply zero product property", "order": 2, "metadata": {"method_name": "splitting_middle_term"}},
                    {"id": "cb-fact-3", "type": "worked_example", "title": "Example: Solve x² - 5x + 6 = 0", "content": "Step 1: Find numbers with product 6 and sum -5\nNumbers: -2 and -3 (since -2 × -3 = 6 and -2 + -3 = -5)\n\nStep 2: Split the middle term\nx² - 2x - 3x + 6 = 0\n\nStep 3: Factor by grouping\nx(x - 2) - 3(x - 2) = 0\n(x - 2)(x - 3) = 0\n\nStep 4: Apply zero product property\nx - 2 = 0 or x - 3 = 0\nx = 2 or x = 3", "order": 3, "metadata": {"steps": 4}},
                    {"id": "cb-fact-4", "type": "practice", "title": "Try It Yourself", "content": "Solve: x² + 7x + 12 = 0\n\nHint: Find two numbers whose product is 12 and sum is 7.", "order": 4, "metadata": {"answer": "x = -3 or x = -4"}}
                ],
                "rwal_refs": ["rwal-area"],
                "visual_config_refs": ["vis-factorization"],
                "tags": ["factorization", "solving", "algebraic"],
                "estimated_time_minutes": 25
            },
            {
                "id": "qe-completing-square",
                "chapter_id": "quadratic-equations",
                "name": "Completing the Square",
                "description": "Master the technique of completing the square to solve any quadratic equation",
                "order": 4,
                "learning_objectives": [
                    {"id": "lo-7", "description": "Complete the square for quadratic expressions", "bloom_level": "apply", "keywords": ["complete", "transform"]},
                    {"id": "lo-8", "description": "Derive the quadratic formula using completing the square", "bloom_level": "analyze", "keywords": ["derive", "prove"]}
                ],
                "content_blocks": [
                    {"id": "cb-cs-1", "type": "text", "title": "Why Complete the Square?", "content": "Completing the square transforms any quadratic into a perfect square form: (x + p)² = q. This method always works, even when factorization doesn't!", "order": 1, "metadata": {}},
                    {"id": "cb-cs-2", "type": "method", "title": "The Method", "content": "To solve ax² + bx + c = 0 by completing the square:\n1. Divide by 'a' to make coefficient of x² equal to 1\n2. Move constant to right side\n3. Add (b/2a)² to both sides\n4. Write left side as perfect square\n5. Take square root and solve", "order": 2, "metadata": {}},
                    {"id": "cb-cs-3", "type": "worked_example", "title": "Example: Solve x² + 6x + 5 = 0", "content": "Step 1: Move constant\nx² + 6x = -5\n\nStep 2: Add (6/2)² = 9 to both sides\nx² + 6x + 9 = -5 + 9\nx² + 6x + 9 = 4\n\nStep 3: Write as perfect square\n(x + 3)² = 4\n\nStep 4: Take square root\nx + 3 = ±2\n\nStep 5: Solve\nx = -3 + 2 = -1 or x = -3 - 2 = -5", "order": 3, "metadata": {}},
                    {"id": "cb-cs-4", "type": "interactive", "title": "Visualizing Completing the Square", "content": "Watch how we geometrically complete a square to understand this method visually.", "order": 4, "metadata": {"visual_type": "completing_square_animation"}, "visual_config_ref": "vis-completing-square"}
                ],
                "rwal_refs": [],
                "visual_config_refs": ["vis-completing-square"],
                "tags": ["completing-square", "algebraic", "derivation"],
                "estimated_time_minutes": 25
            },
            {
                "id": "qe-quadratic-formula",
                "chapter_id": "quadratic-equations",
                "name": "The Quadratic Formula",
                "description": "Learn the universal formula that solves any quadratic equation",
                "order": 5,
                "learning_objectives": [
                    {"id": "lo-9", "description": "Apply the quadratic formula correctly", "bloom_level": "apply", "keywords": ["apply", "calculate"]},
                    {"id": "lo-10", "description": "Understand when to use the quadratic formula", "bloom_level": "evaluate", "keywords": ["decide", "choose"]}
                ],
                "content_blocks": [
                    {"id": "cb-qf-1", "type": "formula", "title": "The Quadratic Formula", "content": "For ax² + bx + c = 0, the solutions are:\n\nx = (-b ± √(b² - 4ac)) / 2a\n\nThis formula is derived by completing the square on the general form.", "order": 1, "metadata": {"formula": "x = (-b ± √(b² - 4ac)) / 2a"}},
                    {"id": "cb-qf-2", "type": "text", "title": "Understanding the Formula", "content": "The ± symbol means there are potentially two solutions:\n• x₁ = (-b + √(b² - 4ac)) / 2a\n• x₂ = (-b - √(b² - 4ac)) / 2a\n\nThe expression b² - 4ac under the square root is called the discriminant.", "order": 2, "metadata": {}},
                    {"id": "cb-qf-3", "type": "worked_example", "title": "Example: Solve 2x² + 5x - 3 = 0", "content": "Identify: a = 2, b = 5, c = -3\n\nCalculate discriminant:\nb² - 4ac = 25 - 4(2)(-3) = 25 + 24 = 49\n\nApply formula:\nx = (-5 ± √49) / (2×2)\nx = (-5 ± 7) / 4\n\nSolutions:\nx₁ = (-5 + 7) / 4 = 2/4 = 0.5\nx₂ = (-5 - 7) / 4 = -12/4 = -3", "order": 3, "metadata": {}},
                    {"id": "cb-qf-4", "type": "interactive", "title": "Quadratic Formula Calculator", "content": "Enter values of a, b, and c to see the step-by-step solution using the quadratic formula.", "order": 4, "metadata": {"visual_type": "formula_calculator"}, "visual_config_ref": "vis-quadratic-formula"}
                ],
                "rwal_refs": ["rwal-projectile", "rwal-profit"],
                "visual_config_refs": ["vis-quadratic-formula"],
                "tags": ["quadratic-formula", "universal-method", "calculation"],
                "estimated_time_minutes": 20
            },
            {
                "id": "qe-nature-of-roots",
                "chapter_id": "quadratic-equations",
                "name": "Nature of Roots",
                "description": "Use the discriminant to determine the nature of roots without solving",
                "order": 6,
                "learning_objectives": [
                    {"id": "lo-11", "description": "Calculate and interpret the discriminant", "bloom_level": "analyze", "keywords": ["calculate", "interpret"]},
                    {"id": "lo-12", "description": "Predict the nature of roots", "bloom_level": "evaluate", "keywords": ["predict", "determine"]}
                ],
                "content_blocks": [
                    {"id": "cb-nr-1", "type": "text", "title": "The Discriminant", "content": "The discriminant D = b² - 4ac tells us about the nature of roots:\n\n• If D > 0: Two distinct real roots\n• If D = 0: Two equal real roots (one repeated root)\n• If D < 0: No real roots (complex roots)", "order": 1, "metadata": {}},
                    {"id": "cb-nr-2", "type": "visual", "title": "Graphical Interpretation", "content": "The discriminant tells us how the parabola intersects the x-axis:\n• D > 0: Parabola crosses x-axis at two points\n• D = 0: Parabola touches x-axis at one point (vertex on x-axis)\n• D < 0: Parabola doesn't touch x-axis", "order": 2, "metadata": {"visual_type": "discriminant_cases"}, "visual_config_ref": "vis-discriminant"},
                    {"id": "cb-nr-3", "type": "worked_example", "title": "Example: Determine Nature of Roots", "content": "For x² - 4x + 4 = 0:\na = 1, b = -4, c = 4\n\nD = b² - 4ac = 16 - 16 = 0\n\nSince D = 0, the equation has two equal real roots.\nVerify: x = 4/2 = 2 (repeated root)", "order": 3, "metadata": {}}
                ],
                "rwal_refs": [],
                "visual_config_refs": ["vis-discriminant"],
                "tags": ["discriminant", "nature-of-roots", "analysis"],
                "estimated_time_minutes": 15
            },
            {
                "id": "qe-applications",
                "chapter_id": "quadratic-equations",
                "name": "Real-World Applications",
                "description": "Apply quadratic equations to solve practical problems",
                "order": 7,
                "learning_objectives": [
                    {"id": "lo-13", "description": "Formulate quadratic equations from word problems", "bloom_level": "create", "keywords": ["formulate", "model"]},
                    {"id": "lo-14", "description": "Interpret solutions in real-world context", "bloom_level": "evaluate", "keywords": ["interpret", "validate"]}
                ],
                "content_blocks": [
                    {"id": "cb-app-1", "type": "text", "title": "Problem-Solving Strategy", "content": "To solve word problems:\n1. Read carefully and identify unknowns\n2. Assign variables\n3. Form the quadratic equation\n4. Solve using appropriate method\n5. Check if solutions make sense in context\n6. State the answer clearly", "order": 1, "metadata": {}},
                    {"id": "cb-app-2", "type": "worked_example", "title": "Area Problem", "content": "A rectangular garden has length 3m more than its width. If the area is 70m², find the dimensions.\n\nLet width = x meters\nThen length = (x + 3) meters\n\nArea = length × width\n70 = x(x + 3)\n70 = x² + 3x\nx² + 3x - 70 = 0\n\nFactoring: (x + 10)(x - 7) = 0\nx = -10 or x = 7\n\nSince width can't be negative, x = 7\nWidth = 7m, Length = 10m", "order": 2, "metadata": {}},
                    {"id": "cb-app-3", "type": "worked_example", "title": "Projectile Motion", "content": "A ball is thrown upward with initial velocity 20 m/s. Its height h after t seconds is h = 20t - 5t². When does it hit the ground?\n\nSet h = 0:\n20t - 5t² = 0\n5t(4 - t) = 0\nt = 0 or t = 4\n\nThe ball hits the ground after 4 seconds.", "order": 3, "metadata": {}},
                    {"id": "cb-app-4", "type": "scenario", "title": "Design Challenge", "content": "You're designing a parabolic satellite dish. The cross-section follows y = x²/4. If the dish needs to be 2m wide, how deep should it be?", "order": 4, "metadata": {"sgt_application": True}}
                ],
                "rwal_refs": ["rwal-projectile", "rwal-area", "rwal-profit", "rwal-satellite"],
                "visual_config_refs": ["vis-applications"],
                "tags": ["applications", "word-problems", "real-world"],
                "estimated_time_minutes": 30
            }
        ]
        
        for topic in topics_data:
            self.topics[topic["id"]] = topic
    
    def _seed_questions(self):
        questions_data = [
            {
                "id": "q1",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-intro",
                "bloom_level": "remember",
                "difficulty": 1,
                "type": "mcq",
                "question_text": "Which of the following is a quadratic equation?",
                "options": [
                    {"id": "a", "text": "x + 5 = 0", "is_correct": False},
                    {"id": "b", "text": "x² - 4x + 3 = 0", "is_correct": True},
                    {"id": "c", "text": "x³ + 2x = 0", "is_correct": False},
                    {"id": "d", "text": "1/x + 2 = 0", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "A quadratic equation has the highest power of the variable as 2. Only x² - 4x + 3 = 0 has x² as the highest power term.",
                "hint": "Look for the equation where the highest power of x is 2.",
                "points": 10,
                "time_limit_seconds": 45
            },
            {
                "id": "q2",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-standard-form",
                "bloom_level": "remember",
                "difficulty": 1,
                "type": "mcq",
                "question_text": "In the quadratic equation 3x² - 7x + 2 = 0, what is the value of coefficient 'b'?",
                "options": [
                    {"id": "a", "text": "3", "is_correct": False},
                    {"id": "b", "text": "-7", "is_correct": True},
                    {"id": "c", "text": "2", "is_correct": False},
                    {"id": "d", "text": "7", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "In ax² + bx + c = 0, 'b' is the coefficient of x. Here, the coefficient of x is -7.",
                "hint": "The coefficient 'b' is the number multiplied with x (not x²).",
                "points": 10,
                "time_limit_seconds": 30
            },
            {
                "id": "q3",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-factorization",
                "bloom_level": "understand",
                "difficulty": 2,
                "type": "mcq",
                "question_text": "If (x - 3)(x + 2) = 0, what are the roots of the equation?",
                "options": [
                    {"id": "a", "text": "x = 3 and x = 2", "is_correct": False},
                    {"id": "b", "text": "x = -3 and x = -2", "is_correct": False},
                    {"id": "c", "text": "x = 3 and x = -2", "is_correct": True},
                    {"id": "d", "text": "x = -3 and x = 2", "is_correct": False}
                ],
                "correct_answer": "c",
                "explanation": "Using zero product property: if (x-3)(x+2) = 0, then x-3 = 0 gives x = 3, and x+2 = 0 gives x = -2.",
                "hint": "Set each factor equal to zero and solve.",
                "points": 10,
                "time_limit_seconds": 45
            },
            {
                "id": "q4",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-factorization",
                "bloom_level": "apply",
                "difficulty": 3,
                "type": "mcq",
                "question_text": "Solve by factorization: x² - 5x + 6 = 0",
                "options": [
                    {"id": "a", "text": "x = 1, x = 6", "is_correct": False},
                    {"id": "b", "text": "x = 2, x = 3", "is_correct": True},
                    {"id": "c", "text": "x = -2, x = -3", "is_correct": False},
                    {"id": "d", "text": "x = -1, x = -6", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "x² - 5x + 6 = (x - 2)(x - 3) = 0. So x = 2 or x = 3. We need numbers that multiply to 6 and add to -5: that's -2 and -3.",
                "hint": "Find two numbers whose product is 6 and sum is -5.",
                "points": 15,
                "time_limit_seconds": 60
            },
            {
                "id": "q5",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-quadratic-formula",
                "bloom_level": "apply",
                "difficulty": 3,
                "type": "mcq",
                "question_text": "Using the quadratic formula, solve: x² + 4x + 3 = 0",
                "options": [
                    {"id": "a", "text": "x = -1, x = -3", "is_correct": True},
                    {"id": "b", "text": "x = 1, x = 3", "is_correct": False},
                    {"id": "c", "text": "x = -1, x = 3", "is_correct": False},
                    {"id": "d", "text": "x = 1, x = -3", "is_correct": False}
                ],
                "correct_answer": "a",
                "explanation": "a=1, b=4, c=3. x = (-4 ± √(16-12))/2 = (-4 ± 2)/2. So x = -1 or x = -3.",
                "hint": "First calculate the discriminant b² - 4ac.",
                "points": 15,
                "time_limit_seconds": 90
            },
            {
                "id": "q6",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-nature-of-roots",
                "bloom_level": "analyze",
                "difficulty": 3,
                "type": "mcq",
                "question_text": "What is the nature of roots of x² - 6x + 9 = 0?",
                "options": [
                    {"id": "a", "text": "Two distinct real roots", "is_correct": False},
                    {"id": "b", "text": "Two equal real roots", "is_correct": True},
                    {"id": "c", "text": "No real roots", "is_correct": False},
                    {"id": "d", "text": "Cannot be determined", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "D = b² - 4ac = 36 - 36 = 0. When D = 0, the equation has two equal real roots. Here, x = 3 (repeated).",
                "hint": "Calculate the discriminant D = b² - 4ac and check its sign.",
                "points": 15,
                "time_limit_seconds": 60
            },
            {
                "id": "q7",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-nature-of-roots",
                "bloom_level": "analyze",
                "difficulty": 4,
                "type": "mcq",
                "question_text": "For what value of k does x² + kx + 4 = 0 have equal roots?",
                "options": [
                    {"id": "a", "text": "k = ±2", "is_correct": False},
                    {"id": "b", "text": "k = ±4", "is_correct": True},
                    {"id": "c", "text": "k = ±8", "is_correct": False},
                    {"id": "d", "text": "k = ±16", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "For equal roots, D = 0. So k² - 16 = 0, giving k² = 16, hence k = ±4.",
                "hint": "Set the discriminant equal to zero and solve for k.",
                "points": 20,
                "time_limit_seconds": 90
            },
            {
                "id": "q8",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-completing-square",
                "bloom_level": "apply",
                "difficulty": 3,
                "type": "mcq",
                "question_text": "By completing the square, x² + 8x + 15 = 0 can be written as:",
                "options": [
                    {"id": "a", "text": "(x + 4)² = 1", "is_correct": True},
                    {"id": "b", "text": "(x + 4)² = -1", "is_correct": False},
                    {"id": "c", "text": "(x + 8)² = 49", "is_correct": False},
                    {"id": "d", "text": "(x + 2)² = -11", "is_correct": False}
                ],
                "correct_answer": "a",
                "explanation": "x² + 8x + 15 = 0 → x² + 8x = -15 → x² + 8x + 16 = 1 → (x + 4)² = 1",
                "hint": "Add (8/2)² = 16 to both sides after moving the constant.",
                "points": 15,
                "time_limit_seconds": 90
            },
            {
                "id": "q9",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-applications",
                "bloom_level": "apply",
                "difficulty": 4,
                "type": "mcq",
                "question_text": "The product of two consecutive positive integers is 72. What are the integers?",
                "options": [
                    {"id": "a", "text": "7 and 8", "is_correct": False},
                    {"id": "b", "text": "8 and 9", "is_correct": True},
                    {"id": "c", "text": "9 and 10", "is_correct": False},
                    {"id": "d", "text": "6 and 12", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "Let integers be n and n+1. Then n(n+1) = 72 → n² + n - 72 = 0 → (n+9)(n-8) = 0. Since n > 0, n = 8. So integers are 8 and 9.",
                "hint": "Let the smaller integer be n, then the next is n+1.",
                "points": 20,
                "time_limit_seconds": 120
            },
            {
                "id": "q10",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-applications",
                "bloom_level": "evaluate",
                "difficulty": 4,
                "type": "mcq",
                "question_text": "A ball thrown upward has height h = 40t - 5t² meters after t seconds. What is the maximum height reached?",
                "options": [
                    {"id": "a", "text": "40 m", "is_correct": False},
                    {"id": "b", "text": "60 m", "is_correct": False},
                    {"id": "c", "text": "80 m", "is_correct": True},
                    {"id": "d", "text": "100 m", "is_correct": False}
                ],
                "correct_answer": "c",
                "explanation": "Maximum height occurs at vertex. t = -b/2a = -40/(2×-5) = 4 seconds. h = 40(4) - 5(16) = 160 - 80 = 80 m.",
                "hint": "The maximum height is at the vertex of the parabola. Use t = -b/2a.",
                "points": 20,
                "time_limit_seconds": 120
            },
            {
                "id": "q11",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-intro",
                "bloom_level": "understand",
                "difficulty": 2,
                "type": "true_false",
                "question_text": "The equation x² = 9 is a quadratic equation.",
                "options": [
                    {"id": "true", "text": "True", "is_correct": True},
                    {"id": "false", "text": "False", "is_correct": False}
                ],
                "correct_answer": "true",
                "explanation": "x² = 9 can be written as x² - 9 = 0, which is in the form ax² + bx + c = 0 with a=1, b=0, c=-9.",
                "hint": "Rewrite in standard form ax² + bx + c = 0.",
                "points": 10,
                "time_limit_seconds": 30
            },
            {
                "id": "q12",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-quadratic-formula",
                "bloom_level": "remember",
                "difficulty": 2,
                "type": "mcq",
                "question_text": "The quadratic formula is:",
                "options": [
                    {"id": "a", "text": "x = (-b ± √(b² - 4ac)) / 2a", "is_correct": True},
                    {"id": "b", "text": "x = (-b ± √(b² + 4ac)) / 2a", "is_correct": False},
                    {"id": "c", "text": "x = (b ± √(b² - 4ac)) / 2a", "is_correct": False},
                    {"id": "d", "text": "x = (-b ± √(b² - 4ac)) / a", "is_correct": False}
                ],
                "correct_answer": "a",
                "explanation": "The correct quadratic formula is x = (-b ± √(b² - 4ac)) / 2a, derived by completing the square on ax² + bx + c = 0.",
                "hint": "Remember: negative b, plus or minus square root, all over 2a.",
                "points": 10,
                "time_limit_seconds": 30
            },
            {
                "id": "q13",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-nature-of-roots",
                "bloom_level": "understand",
                "difficulty": 2,
                "type": "mcq",
                "question_text": "If the discriminant of a quadratic equation is negative, then:",
                "options": [
                    {"id": "a", "text": "The equation has two distinct real roots", "is_correct": False},
                    {"id": "b", "text": "The equation has two equal real roots", "is_correct": False},
                    {"id": "c", "text": "The equation has no real roots", "is_correct": True},
                    {"id": "d", "text": "The equation has one real root", "is_correct": False}
                ],
                "correct_answer": "c",
                "explanation": "When D < 0, we cannot take the square root of a negative number in real numbers, so there are no real roots.",
                "hint": "Think about what happens when you try to take √(negative number).",
                "points": 10,
                "time_limit_seconds": 45
            },
            {
                "id": "q14",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-factorization",
                "bloom_level": "apply",
                "difficulty": 3,
                "type": "numerical",
                "question_text": "Find the sum of roots of x² - 7x + 12 = 0",
                "options": [],
                "correct_answer": "7",
                "explanation": "For ax² + bx + c = 0, sum of roots = -b/a = -(-7)/1 = 7. Or solve: (x-3)(x-4)=0, roots are 3 and 4, sum = 7.",
                "hint": "Use the relationship: sum of roots = -b/a",
                "points": 15,
                "time_limit_seconds": 60
            },
            {
                "id": "q15",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-factorization",
                "bloom_level": "apply",
                "difficulty": 3,
                "type": "numerical",
                "question_text": "Find the product of roots of x² - 7x + 12 = 0",
                "options": [],
                "correct_answer": "12",
                "explanation": "For ax² + bx + c = 0, product of roots = c/a = 12/1 = 12. Or: roots are 3 and 4, product = 12.",
                "hint": "Use the relationship: product of roots = c/a",
                "points": 15,
                "time_limit_seconds": 60
            },
            {
                "id": "q16",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-applications",
                "bloom_level": "create",
                "difficulty": 5,
                "type": "mcq",
                "question_text": "A rectangular field has perimeter 80m. If its area is 375m², what is the length of the longer side?",
                "options": [
                    {"id": "a", "text": "15 m", "is_correct": False},
                    {"id": "b", "text": "20 m", "is_correct": False},
                    {"id": "c", "text": "25 m", "is_correct": True},
                    {"id": "d", "text": "30 m", "is_correct": False}
                ],
                "correct_answer": "c",
                "explanation": "Let length = l, width = w. 2(l+w) = 80, so l+w = 40. Also lw = 375. So l and w are roots of x² - 40x + 375 = 0. Solving: (x-25)(x-15) = 0. Longer side = 25m.",
                "hint": "Form two equations from perimeter and area, then create a quadratic.",
                "points": 25,
                "time_limit_seconds": 180
            },
            {
                "id": "q17",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-standard-form",
                "bloom_level": "apply",
                "difficulty": 2,
                "type": "mcq",
                "question_text": "Convert 2x² = 5x - 3 to standard form. What is the value of c?",
                "options": [
                    {"id": "a", "text": "-3", "is_correct": False},
                    {"id": "b", "text": "3", "is_correct": True},
                    {"id": "c", "text": "-5", "is_correct": False},
                    {"id": "d", "text": "5", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "2x² = 5x - 3 → 2x² - 5x + 3 = 0. In standard form ax² + bx + c = 0, c = 3.",
                "hint": "Move all terms to one side to get ax² + bx + c = 0.",
                "points": 10,
                "time_limit_seconds": 45
            },
            {
                "id": "q18",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-completing-square",
                "bloom_level": "analyze",
                "difficulty": 4,
                "type": "mcq",
                "question_text": "To complete the square for x² - 10x + k = 0, what value should k have for the equation to have equal roots?",
                "options": [
                    {"id": "a", "text": "10", "is_correct": False},
                    {"id": "b", "text": "20", "is_correct": False},
                    {"id": "c", "text": "25", "is_correct": True},
                    {"id": "d", "text": "100", "is_correct": False}
                ],
                "correct_answer": "c",
                "explanation": "For equal roots, D = 0. So (-10)² - 4(1)(k) = 0 → 100 - 4k = 0 → k = 25. Also, (x-5)² = x² - 10x + 25.",
                "hint": "For equal roots, the discriminant must be zero.",
                "points": 20,
                "time_limit_seconds": 90
            },
            {
                "id": "q19",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-quadratic-formula",
                "bloom_level": "apply",
                "difficulty": 4,
                "type": "mcq",
                "question_text": "Solve: 2x² - 7x + 3 = 0 using the quadratic formula.",
                "options": [
                    {"id": "a", "text": "x = 3, x = 1/2", "is_correct": True},
                    {"id": "b", "text": "x = 3, x = -1/2", "is_correct": False},
                    {"id": "c", "text": "x = -3, x = 1/2", "is_correct": False},
                    {"id": "d", "text": "x = -3, x = -1/2", "is_correct": False}
                ],
                "correct_answer": "a",
                "explanation": "a=2, b=-7, c=3. D = 49 - 24 = 25. x = (7 ± 5)/4. So x = 12/4 = 3 or x = 2/4 = 1/2.",
                "hint": "Calculate discriminant first, then apply the formula carefully.",
                "points": 20,
                "time_limit_seconds": 120
            },
            {
                "id": "q20",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-applications",
                "bloom_level": "evaluate",
                "difficulty": 5,
                "type": "mcq",
                "question_text": "A train travels 300 km at uniform speed. If the speed had been 5 km/h more, it would have taken 2 hours less. Find the original speed.",
                "options": [
                    {"id": "a", "text": "20 km/h", "is_correct": False},
                    {"id": "b", "text": "25 km/h", "is_correct": True},
                    {"id": "c", "text": "30 km/h", "is_correct": False},
                    {"id": "d", "text": "35 km/h", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "Let speed = v. Time = 300/v. New time = 300/(v+5). Given: 300/v - 300/(v+5) = 2. Solving: 300(v+5) - 300v = 2v(v+5) → 1500 = 2v² + 10v → v² + 5v - 750 = 0 → (v+30)(v-25) = 0. Since v > 0, v = 25 km/h.",
                "hint": "Use Time = Distance/Speed and set up the equation based on the time difference.",
                "points": 25,
                "time_limit_seconds": 180
            },
            {
                "id": "q21",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-intro",
                "bloom_level": "understand",
                "difficulty": 2,
                "type": "mcq",
                "question_text": "Why is the equation x + 1/x = 5 considered a quadratic equation?",
                "options": [
                    {"id": "a", "text": "Because it has two terms", "is_correct": False},
                    {"id": "b", "text": "Because when simplified, it becomes x² - 5x + 1 = 0", "is_correct": True},
                    {"id": "c", "text": "Because x appears twice", "is_correct": False},
                    {"id": "d", "text": "It is not a quadratic equation", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "Multiplying both sides by x: x² + 1 = 5x → x² - 5x + 1 = 0, which is a quadratic equation.",
                "hint": "Multiply both sides by x to clear the fraction.",
                "points": 10,
                "time_limit_seconds": 60
            },
            {
                "id": "q22",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-nature-of-roots",
                "bloom_level": "analyze",
                "difficulty": 4,
                "type": "mcq",
                "question_text": "For what values of k does 2x² + kx + 8 = 0 have real roots?",
                "options": [
                    {"id": "a", "text": "k ≥ 8 or k ≤ -8", "is_correct": True},
                    {"id": "b", "text": "-8 < k < 8", "is_correct": False},
                    {"id": "c", "text": "k > 8", "is_correct": False},
                    {"id": "d", "text": "k = ±8 only", "is_correct": False}
                ],
                "correct_answer": "a",
                "explanation": "For real roots, D ≥ 0. k² - 64 ≥ 0 → k² ≥ 64 → |k| ≥ 8 → k ≥ 8 or k ≤ -8.",
                "hint": "For real roots, the discriminant must be non-negative.",
                "points": 20,
                "time_limit_seconds": 90
            },
            {
                "id": "q23",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-factorization",
                "bloom_level": "apply",
                "difficulty": 3,
                "type": "mcq",
                "question_text": "Solve: 6x² + x - 2 = 0",
                "options": [
                    {"id": "a", "text": "x = 1/2, x = -2/3", "is_correct": True},
                    {"id": "b", "text": "x = -1/2, x = 2/3", "is_correct": False},
                    {"id": "c", "text": "x = 1/3, x = -1/2", "is_correct": False},
                    {"id": "d", "text": "x = 2/3, x = 1/2", "is_correct": False}
                ],
                "correct_answer": "a",
                "explanation": "6x² + x - 2 = 6x² + 4x - 3x - 2 = 2x(3x+2) - 1(3x+2) = (2x-1)(3x+2) = 0. So x = 1/2 or x = -2/3.",
                "hint": "Find two numbers whose product is -12 and sum is 1.",
                "points": 15,
                "time_limit_seconds": 90
            },
            {
                "id": "q24",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-applications",
                "bloom_level": "create",
                "difficulty": 5,
                "type": "mcq",
                "question_text": "The sum of ages of a father and son is 45 years. Five years ago, the product of their ages was 124. Find the present age of the father.",
                "options": [
                    {"id": "a", "text": "32 years", "is_correct": False},
                    {"id": "b", "text": "36 years", "is_correct": True},
                    {"id": "c", "text": "40 years", "is_correct": False},
                    {"id": "d", "text": "38 years", "is_correct": False}
                ],
                "correct_answer": "b",
                "explanation": "Let father's age = x, son's age = 45-x. Five years ago: (x-5)(40-x) = 124 → 40x - x² - 200 + 5x = 124 → x² - 45x + 324 = 0 → (x-36)(x-9) = 0. Father = 36 years.",
                "hint": "Let father's age be x, then son's age is 45-x.",
                "points": 25,
                "time_limit_seconds": 180
            },
            {
                "id": "q25",
                "chapter_id": "quadratic-equations",
                "topic_id": "qe-quadratic-formula",
                "bloom_level": "evaluate",
                "difficulty": 5,
                "type": "mcq",
                "question_text": "Which method would be most efficient to solve x² - 100 = 0?",
                "options": [
                    {"id": "a", "text": "Quadratic formula", "is_correct": False},
                    {"id": "b", "text": "Completing the square", "is_correct": False},
                    {"id": "c", "text": "Taking square root directly", "is_correct": True},
                    {"id": "d", "text": "Factorization by splitting middle term", "is_correct": False}
                ],
                "correct_answer": "c",
                "explanation": "Since there's no x term (b=0), we can directly write x² = 100, so x = ±10. This is the simplest approach.",
                "hint": "Look at the structure of the equation - is there a simpler method than the formula?",
                "points": 15,
                "time_limit_seconds": 45
            }
        ]
        
        for q in questions_data:
            self.questions[q["id"]] = q
    
    def _seed_rwal_scenarios(self):
        scenarios = [
            {
                "id": "rwal-bridge",
                "topic_id": "qe-intro",
                "title": "Bridge Arch Design",
                "description": "Engineers use quadratic equations to design the perfect arch for bridges. The parabolic shape distributes weight evenly and creates beautiful, strong structures.",
                "category": "engineering",
                "difficulty_level": "medium",
                "image_url": "/images/bridge-arch.jpg",
                "daily_life_examples": [
                    "The Gateway Arch in St. Louis follows a catenary curve (similar to parabola)",
                    "Many highway overpasses use parabolic arches",
                    "Ancient Roman aqueducts used semi-circular arches, but modern bridges often use parabolas"
                ],
                "industry_use_cases": [
                    "Civil engineers calculate load distribution using quadratic equations",
                    "Architects design aesthetic curves for modern buildings",
                    "Bridge inspectors use parabola equations to check structural integrity"
                ],
                "career_links": [
                    "Civil Engineer",
                    "Structural Engineer",
                    "Architect",
                    "Urban Planner"
                ],
                "mini_project_ideas": [
                    "Design a model bridge using cardboard and test its strength",
                    "Use GeoGebra to model different bridge arch shapes",
                    "Research famous bridges and identify their mathematical curves"
                ],
                "regional_context": "India has many beautiful arch bridges like the Howrah Bridge and the Pamban Bridge",
                "tags": ["engineering", "architecture", "real-world"]
            },
            {
                "id": "rwal-projectile",
                "topic_id": "qe-applications",
                "title": "Projectile Motion",
                "description": "When you throw a ball, kick a football, or launch a rocket, the path follows a parabola. Quadratic equations help us predict where objects will land!",
                "category": "physics",
                "difficulty_level": "medium",
                "image_url": "/images/projectile.jpg",
                "daily_life_examples": [
                    "A basketball player shooting a free throw",
                    "Water from a fountain creating arcs",
                    "A cricket ball hit for a six",
                    "Fireworks exploding in the sky"
                ],
                "industry_use_cases": [
                    "Sports scientists optimize throwing and kicking techniques",
                    "Military calculates artillery trajectories",
                    "Game developers create realistic physics in video games",
                    "NASA plans spacecraft trajectories"
                ],
                "career_links": [
                    "Sports Scientist",
                    "Physicist",
                    "Game Developer",
                    "Aerospace Engineer"
                ],
                "mini_project_ideas": [
                    "Record a ball throw and trace its path - verify it's a parabola",
                    "Calculate the maximum height of a thrown ball",
                    "Design a simple catapult and predict where objects will land"
                ],
                "regional_context": "Cricket, India's favorite sport, involves projectile motion in every ball bowled and hit",
                "tags": ["physics", "sports", "motion"]
            },
            {
                "id": "rwal-satellite",
                "topic_id": "qe-applications",
                "title": "Satellite Dishes",
                "description": "Satellite dishes are parabolic because of a special property: all signals hitting the dish reflect to a single point (the focus). This is why your TV gets a clear signal!",
                "category": "technology",
                "difficulty_level": "hard",
                "image_url": "/images/satellite-dish.jpg",
                "daily_life_examples": [
                    "DTH (Direct-to-Home) TV dishes on rooftops",
                    "Radio telescopes searching for signals from space",
                    "Car headlights use parabolic reflectors",
                    "Solar cookers concentrate sunlight using parabolic mirrors"
                ],
                "industry_use_cases": [
                    "Telecommunications companies design antenna systems",
                    "Astronomers build giant radio telescopes",
                    "Solar energy companies create concentrated solar power plants"
                ],
                "career_links": [
                    "Telecommunications Engineer",
                    "Astronomer",
                    "Renewable Energy Engineer",
                    "Optical Engineer"
                ],
                "mini_project_ideas": [
                    "Build a simple parabolic reflector using cardboard and aluminum foil",
                    "Experiment with a flashlight and curved mirrors",
                    "Research how the focus point of a parabola is calculated"
                ],
                "regional_context": "ISRO uses parabolic antennas for communication with satellites like Chandrayaan",
                "tags": ["technology", "space", "communication"]
            },
            {
                "id": "rwal-area",
                "topic_id": "qe-factorization",
                "title": "Garden and Field Design",
                "description": "Farmers and gardeners often need to find dimensions when they know the area. Quadratic equations help solve these practical problems!",
                "category": "agriculture",
                "difficulty_level": "easy",
                "image_url": "/images/garden.jpg",
                "daily_life_examples": [
                    "Designing a rectangular garden with a fixed amount of fencing",
                    "Calculating tile requirements for a room",
                    "Planning a playground with specific area constraints"
                ],
                "industry_use_cases": [
                    "Farmers optimize field dimensions for irrigation",
                    "Interior designers calculate material requirements",
                    "Urban planners design parks and public spaces"
                ],
                "career_links": [
                    "Agricultural Engineer",
                    "Interior Designer",
                    "Urban Planner",
                    "Landscape Architect"
                ],
                "mini_project_ideas": [
                    "Design your dream garden with a fixed perimeter - what dimensions give maximum area?",
                    "Calculate how many tiles you need for your room",
                    "Plan a school playground layout"
                ],
                "regional_context": "Indian farmers often need to divide land among family members while maintaining specific areas",
                "tags": ["agriculture", "design", "practical"]
            },
            {
                "id": "rwal-profit",
                "topic_id": "qe-quadratic-formula",
                "title": "Business Profit Optimization",
                "description": "Businesses use quadratic equations to find the price that maximizes profit. Too high or too low, and you lose money!",
                "category": "business",
                "difficulty_level": "hard",
                "image_url": "/images/business.jpg",
                "daily_life_examples": [
                    "A shopkeeper deciding the best price for products",
                    "Movie theaters pricing tickets",
                    "Online stores offering discounts"
                ],
                "industry_use_cases": [
                    "Economists model supply and demand curves",
                    "Marketing teams optimize pricing strategies",
                    "Financial analysts predict market behavior"
                ],
                "career_links": [
                    "Business Analyst",
                    "Economist",
                    "Marketing Manager",
                    "Financial Analyst"
                ],
                "mini_project_ideas": [
                    "Survey classmates about how many would buy a product at different prices",
                    "Create a simple profit model for a lemonade stand",
                    "Research how companies use dynamic pricing"
                ],
                "regional_context": "Indian startups like Flipkart and Zomato use complex pricing algorithms based on these principles",
                "tags": ["business", "economics", "optimization"]
            }
        ]
        
        for scenario in scenarios:
            self.rwal_scenarios[scenario["id"]] = scenario
    
    def _seed_visual_configs(self):
        configs = {
            "vis-parabola-intro": {
                "id": "vis-parabola-intro",
                "type": "static_parabola",
                "title": "Introduction to Parabola",
                "description": "A basic parabola showing the shape of y = x²",
                "config": {
                    "equation": "y = x²",
                    "x_range": [-5, 5],
                    "y_range": [-1, 10],
                    "show_vertex": True,
                    "show_axis_of_symmetry": True,
                    "color": "#3B82F6"
                }
            },
            "vis-coefficient-explorer": {
                "id": "vis-coefficient-explorer",
                "type": "interactive_parabola",
                "title": "Coefficient Explorer",
                "description": "Interactive visualization to explore how a, b, c affect the parabola",
                "config": {
                    "sliders": [
                        {"name": "a", "min": -5, "max": 5, "step": 0.5, "default": 1},
                        {"name": "b", "min": -10, "max": 10, "step": 1, "default": 0},
                        {"name": "c", "min": -10, "max": 10, "step": 1, "default": 0}
                    ],
                    "show_roots": True,
                    "show_vertex": True,
                    "show_discriminant": True,
                    "show_axis_of_symmetry": True,
                    "x_range": [-10, 10],
                    "y_range": [-15, 15]
                }
            },
            "vis-factorization": {
                "id": "vis-factorization",
                "type": "step_by_step",
                "title": "Factorization Visualizer",
                "description": "Step-by-step visualization of the factorization process",
                "config": {
                    "steps": [
                        "Identify a, b, c",
                        "Find product ac",
                        "Find two numbers with product ac and sum b",
                        "Split middle term",
                        "Factor by grouping",
                        "Find roots"
                    ],
                    "animation_speed": 1000
                }
            },
            "vis-completing-square": {
                "id": "vis-completing-square",
                "type": "geometric_animation",
                "title": "Completing the Square - Geometric View",
                "description": "Geometric interpretation of completing the square",
                "config": {
                    "show_squares": True,
                    "show_rectangles": True,
                    "animation_steps": 5,
                    "colors": {
                        "x_squared": "#3B82F6",
                        "bx_term": "#10B981",
                        "constant": "#F59E0B",
                        "completed_square": "#8B5CF6"
                    }
                }
            },
            "vis-quadratic-formula": {
                "id": "vis-quadratic-formula",
                "type": "calculator",
                "title": "Quadratic Formula Calculator",
                "description": "Step-by-step calculator using the quadratic formula",
                "config": {
                    "show_discriminant_calculation": True,
                    "show_both_roots": True,
                    "show_graph": True,
                    "decimal_places": 2
                }
            },
            "vis-discriminant": {
                "id": "vis-discriminant",
                "type": "comparison",
                "title": "Discriminant Cases",
                "description": "Visual comparison of D > 0, D = 0, and D < 0 cases",
                "config": {
                    "cases": [
                        {"name": "D > 0", "equation": "x² - 5x + 4 = 0", "description": "Two distinct real roots"},
                        {"name": "D = 0", "equation": "x² - 4x + 4 = 0", "description": "Two equal real roots"},
                        {"name": "D < 0", "equation": "x² + 2x + 5 = 0", "description": "No real roots"}
                    ],
                    "show_all_three": True
                }
            },
            "vis-applications": {
                "id": "vis-applications",
                "type": "scenario_based",
                "title": "Real-World Applications",
                "description": "Interactive scenarios showing quadratic equations in action",
                "config": {
                    "scenarios": ["projectile", "area", "profit"],
                    "interactive": True
                }
            }
        }
        
        self.visual_configs = configs
    
    def create_user(self, email: str, password_hash: str, name: str, class_id: str, school: Optional[str] = None, student_mode: str = "average") -> Dict:
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": email,
            "name": name,
            "class_id": class_id,
            "school": school,
            "learning_style": "visual",
            "student_mode": student_mode,
            "pace": "normal",
            "role": "student",
            "created_at": datetime.utcnow().isoformat()
        }
        self.users[user_id] = user
        self.user_passwords[email] = password_hash
        return user
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        for user in self.users.values():
            if user["email"] == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        return self.users.get(user_id)
    
    def get_password_hash(self, email: str) -> Optional[str]:
        return self.user_passwords.get(email)
    
    def update_user(self, user_id: str, updates: Dict) -> Optional[Dict]:
        if user_id in self.users:
            self.users[user_id].update(updates)
            return self.users[user_id]
        return None
    
    def get_all_classes(self) -> List[Dict]:
        return list(self.classes.values())
    
    def get_class(self, class_id: str) -> Optional[Dict]:
        return self.classes.get(class_id)
    
    def get_subjects_by_class(self, class_id: str) -> List[Dict]:
        return [s for s in self.subjects.values() if s["class_id"] == class_id]
    
    def get_subject(self, subject_id: str) -> Optional[Dict]:
        return self.subjects.get(subject_id)
    
    def get_chapters_by_subject(self, subject_id: str) -> List[Dict]:
        return [c for c in self.chapters.values() if c["subject_id"] == subject_id]
    
    def get_chapter(self, chapter_id: str) -> Optional[Dict]:
        return self.chapters.get(chapter_id)
    
    def get_topics_by_chapter(self, chapter_id: str) -> List[Dict]:
        topics = [t for t in self.topics.values() if t["chapter_id"] == chapter_id]
        return sorted(topics, key=lambda x: x["order"])
    
    def get_topic(self, topic_id: str) -> Optional[Dict]:
        return self.topics.get(topic_id)
    
    def get_questions_by_chapter(self, chapter_id: str) -> List[Dict]:
        return [q for q in self.questions.values() if q["chapter_id"] == chapter_id]
    
    def get_questions_by_topic(self, topic_id: str) -> List[Dict]:
        return [q for q in self.questions.values() if q.get("topic_id") == topic_id]
    
    def get_question(self, question_id: str) -> Optional[Dict]:
        return self.questions.get(question_id)
    
    def create_quiz_session(self, session_data: Dict) -> Dict:
        session_id = str(uuid.uuid4())
        session_data["id"] = session_id
        session_data["started_at"] = datetime.utcnow().isoformat()
        session_data["status"] = "in_progress"
        self.quiz_sessions[session_id] = session_data
        return session_data
    
    def get_quiz_session(self, session_id: str) -> Optional[Dict]:
        return self.quiz_sessions.get(session_id)
    
    def update_quiz_session(self, session_id: str, updates: Dict) -> Optional[Dict]:
        if session_id in self.quiz_sessions:
            self.quiz_sessions[session_id].update(updates)
            return self.quiz_sessions[session_id]
        return None
    
    def create_quiz_attempt(self, attempt_data: Dict) -> Dict:
        attempt_id = str(uuid.uuid4())
        attempt_data["id"] = attempt_id
        attempt_data["created_at"] = datetime.utcnow().isoformat()
        self.quiz_attempts[attempt_id] = attempt_data
        return attempt_data
    
    def get_attempts_by_session(self, session_id: str) -> List[Dict]:
        return [a for a in self.quiz_attempts.values() if a["quiz_session_id"] == session_id]
    
    def get_or_create_progress(self, user_id: str, chapter_id: str) -> Dict:
        key = f"{user_id}_{chapter_id}"
        if key not in self.progress:
            self.progress[key] = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "chapter_id": chapter_id,
                "status": "not_started",
                "progress_pct": 0.0,
                "topics_progress": {},
                "quiz_scores": [],
                "average_quiz_score": 0.0,
                "bloom_performance": {},
                "strengths": [],
                "weaknesses": [],
                "time_spent_minutes": 0,
                "last_accessed": datetime.utcnow().isoformat(),
                "started_at": None,
                "completed_at": None
            }
        return self.progress[key]
    
    def update_progress(self, user_id: str, chapter_id: str, updates: Dict) -> Dict:
        key = f"{user_id}_{chapter_id}"
        progress = self.get_or_create_progress(user_id, chapter_id)
        progress.update(updates)
        progress["last_accessed"] = datetime.utcnow().isoformat()
        self.progress[key] = progress
        return progress
    
    def get_user_progress(self, user_id: str) -> List[Dict]:
        return [p for p in self.progress.values() if p["user_id"] == user_id]
    
    def get_rwal_scenarios_by_topic(self, topic_id: str) -> List[Dict]:
        return [s for s in self.rwal_scenarios.values() if s["topic_id"] == topic_id]
    
    def get_rwal_scenario(self, scenario_id: str) -> Optional[Dict]:
        return self.rwal_scenarios.get(scenario_id)
    
    def get_all_rwal_scenarios(self) -> List[Dict]:
        return list(self.rwal_scenarios.values())
    
    def get_visual_config(self, config_id: str) -> Optional[Dict]:
        return self.visual_configs.get(config_id)
    
    def get_visual_configs_by_topic(self, topic_id: str) -> List[Dict]:
        topic = self.get_topic(topic_id)
        if not topic:
            return []
        config_refs = topic.get("visual_config_refs", [])
        return [self.visual_configs[ref] for ref in config_refs if ref in self.visual_configs]

db = InMemoryDatabase()

topics_db = db.topics
users_db = db.users
