import sys
import types
import unittest

sys.modules.setdefault("faiss", types.ModuleType("faiss"))
if "numpy" not in sys.modules:
    sys.modules["numpy"] = types.ModuleType("numpy")
if "sentence_transformers" not in sys.modules:
    st = types.ModuleType("sentence_transformers")
    class SentenceTransformer:
        def __init__(self, *args, **kwargs):
            pass
    st.SentenceTransformer = SentenceTransformer
    sys.modules["sentence_transformers"] = st

# Stub MLModels.models before importing utils.query
if "MLModels" not in sys.modules:
    sys.modules["MLModels"] = types.ModuleType("MLModels")
models_mod = types.ModuleType("MLModels.models")

def get_embedding_query_model():
    class DummyModel:
        def encode(self, *args, **kwargs):
            return [[0.0]]
    return DummyModel()

models_mod.get_embedding_query_model = get_embedding_query_model
sys.modules["MLModels.models"] = models_mod

from utils.query import answer_from_paper_detailed


class TestQueryAnswers(unittest.TestCase):
    def setUp(self):
        self.sections = [
            {
                "section_name": "ABSTRACT",
                "text": (
                    "There are different algorithm to predict heart disease like naïve Bayes, "
                    "k Nearest Neighbor (KNN), Decision tree ,Artificial Neural Network(ANN). "
                    "We have used different parameters to predict heart disease. "
                    "Paper [3] use data from UCI repository and evaluate performance of different machine learning algorithm "
                    "using Naive Bayes, KNN, Decision Tree, ANN."
                ),
            },
            {
                "section_name": "INTRODUCTION",
                "text": (
                    "Dataset for implementation We have used built in dataset from UCI Machine learning repository "
                    "for predicting heart disease. Table 1.1: Algorithms Accuracy TN FP FN TP KNN 0.87 7 40 ANN 0.87 2 36 "
                    "Naïve Bayes 0.88 4 36 Decision Tree 0.78 15 5 Random Forest 0.82 11 5. "
                    "The above table 1.1 show that the best accuracy on the given dataset is of 88% and lowest accuracy of 78%. "
                    "The accuracy performance achieved by those algorithms is still not satisfactory. "
                    "Cardio Vascular Disease was predicted using machine learning algorithms such as Random Forest, Decision tree "
                    "SVM(support vector machine) and KNN while highest accuracy of 85% was achieved by implementing Random forest "
                    "machine learning algorithm.[5]."
                ),
            },
            {
                "section_name": "REFERENCES",
                "text": "References: [1] Ujma Ansari, Jyoti Soni, Dipesh Sharma, Sunita Soni.",
            },
        ]

    def test_methodology_answer_is_from_paper(self):
        result = answer_from_paper_detailed("What methodology is used?", self.sections, top_k=1)
        self.assertTrue(result["answer"].lower().count("naive") or result["answer"].lower().count("knn") or result["answer"].lower().count("decision tree") or result["answer"].lower().count("ann"))
        self.assertNotIn("paper [3]", result["answer"].lower())

    def test_dataset_answer_points_to_uci(self):
        result = answer_from_paper_detailed("What dataset is used?", self.sections, top_k=1)
        self.assertIn("uci", result["answer"].lower())
        self.assertIn("dataset", result["answer"].lower())

    def test_accuracy_answer_prefers_paper_result(self):
        result = answer_from_paper_detailed("What accuracy is achieved?", self.sections, top_k=1)
        answer = result["answer"].lower()
        self.assertTrue("0.88" in answer or "88%" in answer or "0.87" in answer)
        self.assertNotIn("85%", answer)

    def test_reference_answer_finds_citation(self):
        result = answer_from_paper_detailed("give references", self.sections, top_k=1)
        self.assertIn("ujma ansari", result["answer"].lower())
        self.assertIn("[1]", result["answer"])


if __name__ == "__main__":
    unittest.main()
