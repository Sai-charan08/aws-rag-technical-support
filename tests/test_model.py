import time
import pytest
from src.models.intent_classifier import IntentClassifier, get_intent_classifier

@pytest.fixture(scope="module")
def classifier():
    return get_intent_classifier()

def test_classifier_initialization(classifier):
    assert classifier is not None
    assert classifier.vectorizer is not None
    assert classifier.intent_clf is not None

def test_inference_speed(classifier):
    # Warm-up run (Cython / BLAS initialization)
    _ = classifier.predict("Warmup query")
    
    # Test sub-20ms requirement across multiple runs
    start = time.perf_counter()
    res = classifier.predict("How do I fix NoSuchBucket error in S3?")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 20.0  # Ultra-fast inference (< 20ms)
    assert res["latency_ms"] < 20.0
    assert "intent" in res
    assert "service" in res
    assert "urgency" in res

def test_troubleshooting_ec2(classifier):
    res = classifier.predict("How do I fix a Permission denied (publickey) error when connecting to EC2?")
    assert res["service"] == "Amazon EC2"
    assert res["intent"] == "TROUBLESHOOTING"
    assert res["is_out_of_scope"] is False

def test_s3_classification(classifier):
    res = classifier.predict("How do I troubleshoot a NoSuchBucket error in Amazon S3?")
    assert res["service"] == "Amazon S3"
    assert res["intent"] == "TROUBLESHOOTING"
    assert res["is_out_of_scope"] is False

def test_lambda_classification(classifier):
    res = classifier.predict("Task timed out after 3.00 seconds in AWS Lambda")
    assert res["service"] == "AWS Lambda"
    assert res["intent"] == "TROUBLESHOOTING"
    assert res["urgency"] in ("CRITICAL", "HIGH")

def test_iam_least_privilege(classifier):
    res = classifier.predict("What is the Principle of Least Privilege in AWS IAM?")
    assert res["service"] == "AWS IAM"
    assert res["intent"] in ("SECURITY_BEST_PRACTICE", "CONCEPTUAL_EXPLANATION")

def test_cli_generation(classifier):
    res = classifier.predict("Give me the aws s3 sync command to copy local files")
    assert res["intent"] == "CLI_SCRIPT_GENERATION"
    assert res["service"] == "Amazon S3"

def test_out_of_scope_query(classifier):
    res = classifier.predict("How do I deploy an application on Azure Virtual Machines?")
    assert res["is_out_of_scope"] is True
    assert res["intent"] == "OUT_OF_SCOPE"

def test_greeting_interaction(classifier):
    res = classifier.predict("hello")
    assert res["intent"] == "GREETING"
    assert res["service"] == "General AWS"
    assert res["is_out_of_scope"] is False

def test_friendly_solution_model():
    from src.models.solution_model import get_solution_model
    sm = get_solution_model()
    sol_hello = sm.get_exact_solution("hello")
    assert sol_hello is not None
    assert "Hello!" in sol_hello
    assert "AWS Technical Support Assistant" in sol_hello

    sol_s3 = sm.get_exact_solution("How do I fix a NoSuchBucket error in Amazon S3?")
    assert sol_s3 is not None
    assert "Hello!" in sol_s3
    assert "NoSuchBucket" in sol_s3
