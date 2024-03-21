from random import shuffle
import sys
from typing import Dict, Iterator, List

import PyQt6.QtCore as Qc
import PyQt6.QtGui as Qg
import PyQt6.QtWidgets as Qt

# Constants and characters
HIRAGANA_CHARACTERS: Dict[str, str] = {
    "あ": "a",  "い": "i",  "う": "u",  "え": "e",  "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "だ": "da", "ぢ": "ji", "づ": "dzu", "で": "de", "ど": "do",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "を": "wo",
    "ん": "n"
}
KATAKANA_CHARACTERS: Dict[str, str] = {
    "ア": "a",  "イ": "i",  "ウ": "u",  "エ": "e",  "オ": "o",
    "カ": "ka", "キ": "ki", "ク": "ku", "ケ": "ke", "コ": "ko",
    "ガ": "ga", "ギ": "gi", "グ": "gu", "ゲ": "ge", "ゴ": "go",
    "サ": "sa", "シ": "shi", "ス": "su", "セ": "se", "ソ": "so",
    "ザ": "za", "ジ": "ji", "ズ": "zu", "ゼ": "ze", "ゾ": "zo",
    "タ": "ta", "チ": "chi", "ツ": "tsu", "テ": "te", "ト": "to",
    "ダ": "da", "ヂ": "ji", "ヅ": "dzu", "デ": "de", "ド": "do",
    "ナ": "na", "ニ": "ni", "ヌ": "nu", "ネ": "ne", "ノ": "no",
    "ハ": "ha", "ヒ": "hi", "フ": "fu", "ヘ": "he", "ホ": "ho",
    "バ": "ba", "ビ": "bi", "ブ": "bu", "ベ": "be", "ボ": "bo",
    "パ": "pa", "ピ": "pi", "プ": "pu", "ペ": "pe", "ポ": "po",
    "マ": "ma", "ミ": "mi", "ム": "mu", "メ": "me", "モ": "mo",
    "ヤ": "ya",             "ユ": "yu",             "ヨ": "yo",
    "ラ": "ra", "リ": "ri", "ル": "ru", "レ": "re", "ロ": "ro",
    "ワ": "wa", "ヲ": "wo",
    "ン": "n"
}
FONT_SIZE: int = 13
RIGHT_MARGIN_FOR_MSG_BOX: int = 16
MIN_WIDTH: int = 250
MIN_HEIGHT: int = 150
RESPONSE_MSG_BOX_WIDTH: int = 200
RESPONSE_MSG_BOX_HEIGHT: int = 30

# Starting Qt
app = Qt.QApplication(sys.argv)
app.setFont(Qg.QFont("Arial", FONT_SIZE))


class MainApp(Qt.QMainWindow):
    """
    The class corresponding to the main window of the app, in which both the question and the answer fields are located
    """
    answers: Qt.QLineEdit
    current_letter: str
    layout: Qt.QVBoxLayout
    max_size: Qc.QSize
    question: Qt.QLabel
    questions: List[str]
    questions_iterator: Iterator
    score: int
    test_list: Dict[str, str]
    wrong_answers: List[str]

    def __init__(self):
        super(MainApp, self).__init__()
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)

        # The main window - question's text and answer input box, as well as a confirmation button
        self.layout = Qt.QVBoxLayout()
        self.question = Qt.QLabel()
        self.answers = Qt.QLineEdit()
        self.answers.returnPressed.connect(self.on_confirm)  # So the answer gets checked when Enter is pressed
        self.layout.addWidget(self.question)
        self.layout.addWidget(self.answers)
        widget = Qt.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.max_size = self.screen().availableSize()
        self.move((self.max_size.width() - MIN_WIDTH) // 2, (self.max_size.height() - MIN_HEIGHT) // 2)

        # Introductory popup - choosing Hiragana or Katakana
        msg = Qt.QMessageBox()
        msg.setWindowTitle("ひらがな / カタカナ Test")
        msg.setText("テストを始めましょう！\nLet's begin the test!")
        msg.addButton("ひらがな", Qt.QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("カタカナ", Qt.QMessageBox.ButtonRole.RejectRole)
        msg.accepted.connect(self.hiragana_setup)
        msg.rejected.connect(self.katakana_setup)
        self.wrong_answers = []
        msg.layout().setContentsMargins(
            msg.layout().contentsMargins().left(),
            msg.layout().contentsMargins().top(),
            msg.layout().contentsMargins().right() + RIGHT_MARGIN_FOR_MSG_BOX,
            msg.layout().contentsMargins().bottom()
        )
        msg.exec()

    def hiragana_setup(self):
        self.setWindowTitle("ひらがな Test")
        self.test_list = HIRAGANA_CHARACTERS
        self.questions = list(self.test_list.keys())
        shuffle(self.questions)
        self.questions_iterator = iter(self.questions)
        self.score = 0
        self.new_question()

    def katakana_setup(self):
        self.setWindowTitle("カタカナ Test")
        self.test_list = KATAKANA_CHARACTERS
        self.questions = list(self.test_list.keys())
        shuffle(self.questions)
        self.questions_iterator = iter(self.questions)
        self.score = 0
        self.new_question()

    def new_question(self):
        self.current_letter = next(self.questions_iterator, "END")
        if self.current_letter == "END":
            self.end()
        self.question.clear()
        self.answers.clear()
        self.question.setText(u"What is the letter  {0}  ?".format(self.current_letter))

    def on_confirm(self):
        guess = self.answers.text().lower()
        response = Qt.QMessageBox()
        response.setMinimumSize(170, 30)
        response.setWindowTitle("Result")
        response.addButton("Next", Qt.QMessageBox.ButtonRole.AcceptRole)
        response.addButton("Finish", Qt.QMessageBox.ButtonRole.RejectRole)
        if guess == self.test_list[self.current_letter]:
            response.setText("Correct!")
            self.score += 1
        else:
            response.setText(u"Wrong! That is \"{0}\"".format(self.test_list[self.current_letter]))
            self.wrong_answers.append(self.current_letter)
        response.rejected.connect(self.end)
        response.accepted.connect(self.new_question)
        response.move(self.x() + (self.width() - RESPONSE_MSG_BOX_WIDTH) // 2,
                      self.y() + self.height() + RESPONSE_MSG_BOX_HEIGHT)
        response.layout().setContentsMargins(
            response.layout().contentsMargins().left(),
            response.layout().contentsMargins().top(),
            response.layout().contentsMargins().right() + RIGHT_MARGIN_FOR_MSG_BOX,
            response.layout().contentsMargins().bottom()
        )
        response.exec()

    def end(self):
        end_result = Qt.QMessageBox(parent=self)
        end_result.setWindowTitle("Final results")
        text = f"The end! Your score: {self.score}/{len(self.test_list)}"
        if self.score > 0:
            text += ", congratulations!"
        else:
            text += "..."
        if self.wrong_answers:
            text += "\n\nLetters you had problems with: " + ", ".join(self.wrong_answers)
        end_result.setText(text)
        end_result.addButton(Qt.QMessageBox.StandardButton.Ok)
        end_result.destroyed.connect(self.close)
        end_result.accepted.connect(self.close)
        end_result.layout().setContentsMargins(
            end_result.layout().contentsMargins().left(),
            end_result.layout().contentsMargins().top(),
            end_result.layout().contentsMargins().right() + RIGHT_MARGIN_FOR_MSG_BOX,
            end_result.layout().contentsMargins().bottom()
        )
        end_result.exec()


# Exam time
window = MainApp()
window.show()
app.exec()
