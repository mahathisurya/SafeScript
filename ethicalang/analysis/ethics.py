"""
Ethics Checker for EthicaLang

Enforces ethical constraints on code by requiring explicit annotations
for sensitive operations and detecting potentially harmful patterns.

Key Features:
- Detects sensitive function calls (data collection, user tracking, etc.)
- Requires explicit consent annotations
- Identifies dark patterns and manipulative code
- Maintains a registry of disallowed operations
"""

from typing import List, Dict, Set
from ..ast.nodes import *


class EthicalViolation(Exception):
    """Raised when code violates ethical constraints"""
    pass


class EthicsChecker(ASTVisitor):
    """
    Checks code for ethical violations
    
    This analyzer identifies potentially harmful patterns and ensures
    that sensitive operations have proper annotations.
    """
    
    # Sensitive function patterns that require user consent
    REQUIRES_CONSENT = {
        'collect_location', 'get_gps', 'track_location', 'get_location',
        'collect_biometric', 'get_fingerprint', 'get_face', 'scan_face',
        'record_audio', 'access_microphone', 'record_video', 'access_camera',
        'collect_contacts', 'read_contacts', 'access_contacts',
        'read_messages', 'access_messages', 'read_sms',
        'track_user', 'track_behavior', 'log_activity', 'monitor_user',
        'collect_data', 'collect_personal_info', 'gather_user_data',
    }
    
    # Operations that require data protection
    REQUIRES_DATA_PROTECTION = {
        'store_password', 'save_password', 'store_credential',
        'store_payment', 'process_payment', 'save_card',
        'store_ssn', 'store_personal_id', 'save_sensitive_data',
    }
    
    # Disallowed operations (facial recognition, dark patterns, etc.)
    DISALLOWED_OPERATIONS = {
        'facial_recognition': 'Facial recognition systems are ethically problematic',
        'emotion_detection': 'Emotion detection from faces is ethically problematic',
        'deepfake': 'Deepfake generation is prohibited',
        'manipulate_ui': 'UI manipulation (dark patterns) is prohibited',
        'hide_unsubscribe': 'Hiding unsubscribe options is a dark pattern',
        'fake_urgency': 'Creating fake urgency is manipulative',
        'confuse_user': 'Deliberately confusing users is unethical',
        'trick_into_purchase': 'Tricking users into purchases is prohibited',
        'hidden_charges': 'Hidden charges are unethical',
    }
    
    # Required annotations for sensitive operations
    REQUIRED_ANNOTATIONS = {
        'requires_user_consent': REQUIRES_CONSENT,
        'requires_data_protection': REQUIRES_DATA_PROTECTION,
    }
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize the ethics checker
        
        Args:
            strict_mode: If True, enforce all rules strictly
        """
        self.strict_mode = strict_mode
        self.violations = []
        self.current_function = None
        self.current_annotations = []
    
    def analyze(self, ast: Program) -> Dict[str, any]:
        """
        Analyze the entire program for ethical violations
        
        Returns:
            Dictionary with analysis results
        """
        self.violations = []
        
        try:
            self.visit(ast)
        except EthicalViolation:
            pass  # Violations are collected
        
        return {
            'passed': len(self.violations) == 0,
            'violations': self.violations,
            'strict_mode': self.strict_mode
        }
    
    def add_violation(self, violation_type: str, message: str, details: Dict = None):
        """Add an ethical violation"""
        violation = {
            'type': violation_type,
            'message': message,
            'function': self.current_function
        }
        if details:
            violation.update(details)
        self.violations.append(violation)
        
        if self.strict_mode:
            raise EthicalViolation(message)
    
    def visit_Program(self, node: Program):
        """Visit program node"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_FunctionDef(self, node: FunctionDef):
        """Visit function definition"""
        old_function = self.current_function
        old_annotations = self.current_annotations
        
        self.current_function = node.name
        self.current_annotations = [ann.name for ann in node.annotations]
        
        # Check if function name suggests sensitive operation
        self._check_function_name(node.name, node.annotations)
        
        # Visit function body
        for stmt in node.body:
            self.visit(stmt)
        
        self.current_function = old_function
        self.current_annotations = old_annotations
    
    def _check_function_name(self, function_name: str, annotations: List[Annotation]):
        """Check if function name requires specific annotations"""
        annotation_names = [ann.name for ann in annotations]
        
        # Check for consent-requiring operations
        if function_name in self.REQUIRES_CONSENT:
            if 'requires_user_consent' not in annotation_names:
                self.add_violation(
                    'missing_consent_annotation',
                    f'Function "{function_name}" collects sensitive data but lacks @requires_user_consent annotation',
                    {'required_annotation': 'requires_user_consent'}
                )
        
        # Check for data protection operations
        if function_name in self.REQUIRES_DATA_PROTECTION:
            if 'requires_data_protection' not in annotation_names:
                self.add_violation(
                    'missing_protection_annotation',
                    f'Function "{function_name}" handles sensitive data but lacks @requires_data_protection annotation',
                    {'required_annotation': 'requires_data_protection'}
                )
        
        # Check for disallowed operations
        for disallowed, reason in self.DISALLOWED_OPERATIONS.items():
            if disallowed in function_name.lower():
                self.add_violation(
                    'disallowed_operation',
                    f'Function "{function_name}" performs disallowed operation: {reason}',
                    {'operation': disallowed}
                )
    
    def visit_FunctionCall(self, node: FunctionCall):
        """Visit function call"""
        # Check if calling sensitive functions
        if isinstance(node.function, Variable):
            func_name = node.function.name
            
            # Check for consent-requiring calls
            if func_name in self.REQUIRES_CONSENT:
                if 'requires_user_consent' not in self.current_annotations:
                    self.add_violation(
                        'unauthorized_sensitive_call',
                        f'Calling "{func_name}" requires the containing function to have @requires_user_consent',
                        {'called_function': func_name}
                    )
            
            # Check for data protection calls
            if func_name in self.REQUIRES_DATA_PROTECTION:
                if 'requires_data_protection' not in self.current_annotations:
                    self.add_violation(
                        'unauthorized_data_operation',
                        f'Calling "{func_name}" requires the containing function to have @requires_data_protection',
                        {'called_function': func_name}
                    )
            
            # Check for disallowed operations
            for disallowed, reason in self.DISALLOWED_OPERATIONS.items():
                if disallowed in func_name.lower():
                    self.add_violation(
                        'disallowed_operation_call',
                        f'Calling "{func_name}": {reason}',
                        {'operation': disallowed}
                    )
        
        # Visit function and arguments
        self.visit(node.function)
        for arg in node.arguments:
            self.visit(arg)
    
    def visit_Assignment(self, node: Assignment):
        """Visit assignment"""
        # Check for suspicious variable names that might indicate data collection
        suspicious_names = ['password', 'ssn', 'credit_card', 'secret_key', 'api_key']
        for suspicious in suspicious_names:
            if suspicious in node.name.lower():
                if 'requires_data_protection' not in self.current_annotations:
                    self.add_violation(
                        'unprotected_sensitive_data',
                        f'Variable "{node.name}" appears to contain sensitive data but function lacks @requires_data_protection',
                        {'variable': node.name, 'hint': suspicious}
                    )
        
        self.visit(node.value)
    
    def visit_Variable(self, node: Variable):
        """Visit variable reference"""
        pass
    
    def visit_BinaryOp(self, node: BinaryOp):
        """Visit binary operation"""
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_UnaryOp(self, node: UnaryOp):
        """Visit unary operation"""
        self.visit(node.operand)
    
    def visit_Literal(self, node: Literal):
        """Visit literal value"""
        # Check for hardcoded sensitive strings
        if node.type_name == 'string':
            value_lower = str(node.value).lower()
            if any(keyword in value_lower for keyword in ['password', 'secret', 'api_key', 'token']):
                self.add_violation(
                    'hardcoded_secret',
                    f'Potential hardcoded secret detected: "{node.value[:20]}..."',
                    {'value_preview': str(node.value)[:30]}
                )
    
    def visit_ListLiteral(self, node: ListLiteral):
        """Visit list literal"""
        for elem in node.elements:
            self.visit(elem)
    
    def visit_DictLiteral(self, node: DictLiteral):
        """Visit dictionary literal"""
        for key, value in node.pairs:
            self.visit(key)
            self.visit(value)
    
    def visit_IfStatement(self, node: IfStatement):
        """Visit if statement"""
        self.visit(node.condition)
        for stmt in node.then_body:
            self.visit(stmt)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
    
    def visit_WhileLoop(self, node: WhileLoop):
        """Visit while loop"""
        self.visit(node.condition)
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_ForLoop(self, node: ForLoop):
        """Visit for loop"""
        self.visit(node.iterable)
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_ReturnStatement(self, node: ReturnStatement):
        """Visit return statement"""
        if node.value:
            self.visit(node.value)
    
    def visit_MemberAccess(self, node: MemberAccess):
        """Visit member access"""
        self.visit(node.object)
    
    def visit_IndexAccess(self, node: IndexAccess):
        """Visit index access"""
        self.visit(node.object)
        self.visit(node.index)
    
    def visit_Annotation(self, node: Annotation):
        """Visit annotation"""
        pass


def format_ethics_report(results: Dict) -> str:
    """
    Format ethics analysis results into a human-readable report
    
    Args:
        results: Results from EthicsChecker.analyze()
    
    Returns:
        Formatted string report
    """
    if results['passed']:
        return "✓ Ethics check passed: No violations detected"
    
    report = ["❌ Ethics check failed:\n"]
    for i, violation in enumerate(results['violations'], 1):
        report.append(f"{i}. {violation['type'].upper()}")
        report.append(f"   {violation['message']}")
        if violation.get('function'):
            report.append(f"   Function: {violation['function']}")
        report.append("")
    
    return "\n".join(report)
