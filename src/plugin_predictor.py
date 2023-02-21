
import argparse
import sys
from pathlib import Path
from typing import List

from predict_tactic import loadPredictorByFile
from models.tactic_predictor import TacticPredictor
from coq_serapy.contexts import TacticContext

def get_predictor(parser: argparse.ArgumentParser,
                  args: argparse.Namespace) -> TacticPredictor:
    predictor: TacticPredictor
    predictor = loadPredictorByFile(args.weightsfile)
    return predictor

def predict(args: List[str]) -> None:
    parser = argparse.ArgumentParser(
        description="Proverbot9001 interactive prediction model")
    parser.add_argument("weightsfile", default=None, type=Path)
    parser.add_argument("-k", "--num-predictions", default=5)
    parser.add_argument("--print-certainties", action='store_true')
    parser.add_argument("--rel_lemmas", default=[], type=List[str])
    parser.add_argument("--prev_tactics", default=[], type=List[str])
    parser.add_argument("--hypotheses", default=[], type=List[str])
    parser.add_argument("--goal", default="", type=str)
    arg_values = parser.parse_args(args)

    predictor = get_predictor(parser, arg_values)

    while True:
        
        

        if goal.strip() == "":
                print("Exiting...")
                break
        
        tac_context = TacticContext(rel_lemmas,
                                    prev_tactics,
                                    hypotheses,
                                    goal)

        predictions = predictor.predictKTactics(
            tac_context, arg_values.num_predictions)

        for prediction in predictions:
            if arg_values.print_certainties:
                print(f"Prediction: \"{prediction.prediction}\"; "
                      f"certainty: {prediction.certainty}")
            else:
                print(prediction.prediction)

if __name__ == "__main__":
    pass
