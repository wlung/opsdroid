
import asynctest
import asynctest.mock as amock

from opsdroid.core import OpsDroid
from opsdroid.matchers import match_regex
from opsdroid.message import Message
from opsdroid.parsers.regex import parse_regex


class TestParserRegex(asynctest.TestCase):
    """Test the opsdroid regex parser."""

    async def test_parse_regex(self):
        with OpsDroid() as opsdroid:
            mock_skill = amock.CoroutineMock()
            match_regex(r"(.*)")(mock_skill)

            mock_connector = amock.CoroutineMock()
            message = Message("Hello world", "user", "default", mock_connector)

            skills = await parse_regex(opsdroid, message)
            self.assertEqual(mock_skill, skills[0]["skill"])

    async def test_parse_regex_priority(self):
        with OpsDroid() as opsdroid:
            regex = r"(.*)"

            mock_skill_low = amock.CoroutineMock()
            match_regex(regex, score_factor=0.6)(mock_skill_low)

            mock_skill_high = amock.CoroutineMock()
            match_regex(regex, score_factor=1)(mock_skill_high)

            mock_connector = amock.CoroutineMock()
            message = Message("Hello world", "user", "default", mock_connector)

            skills = await opsdroid.get_ranked_skills(message)
            self.assertEqual(mock_skill_high, skills[0]["skill"])

    async def test_parse_regex_raises(self):
        with OpsDroid() as opsdroid:
            mock_skill = amock.CoroutineMock()
            mock_skill.side_effect = Exception()
            match_regex(r"(.*)")(mock_skill)
            self.assertEqual(len(opsdroid.skills), 1)

            mock_connector = amock.MagicMock()
            mock_connector.respond = amock.CoroutineMock()
            message = Message("Hello world", "user",
                              "default", mock_connector)

            skills = await parse_regex(opsdroid, message)
            self.assertEqual(mock_skill, skills[0]["skill"])
