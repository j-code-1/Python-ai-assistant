# MIT License

# Copyright (c) 2019 Georgios Papachristou

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging


class SkillAnalyzer:
    def __init__(self, weight_measure, similarity_measure, args, sensitivity, db):
        self.logger = logging
        self.weight_measure = weight_measure
        self.similarity_measure = similarity_measure
        self.args = args
        self.vectorizer = self._create_vectorizer()
        self.skills = [i for i in db.get_from_table('skills')]
        self.analyzer_sensitivity = sensitivity

    @property
    def tags(self):
        tags_list = []
        for skill in self.skills:
            tags_list.append(skill['tags'].split(','))
        return [' '.join(tag) for tag in tags_list]

    def extract(self, user_transcript):

        train_tdm = self._train_model()
        test_tdm = self.vectorizer.transform([user_transcript])

        similarities = self.similarity_measure(train_tdm, test_tdm)  # Calculate similarities

        skill_index = similarities.argsort(axis=None)[-1]  # Extract the most similar skill
        if similarities[skill_index] > self.analyzer_sensitivity:
            skill_key = [skill for skill in enumerate(self.skills) if skill[0] == skill_index][0][1]
            return skill_key
        else:
            self.logger.debug('Not extracted skills from user voice transcript')
            return None

    def _create_vectorizer(self):
        """
        Create vectorizer.
        """
        return self.weight_measure(**self.args)

    def _train_model(self):
        """
        Create/train the model.
        """
        return self.vectorizer.fit_transform(self.tags)
