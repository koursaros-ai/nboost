from nboost.plugins.models import resolve_model
from nboost import defaults
import unittest
from random import shuffle


class TestPtBertRerankModelPlugin(unittest.TestCase):
    def setUp(self):
        self.model = resolve_model(
            model_dir='pt-bert-base-uncased-msmarco',
            data_dir=defaults.data_dir,
            model_cls=''
        )
        shuffle(CHOICES)

    def test_rank(self):
        ranks, scores = self.model.rank('O wherefore art thou', CHOICES)
        self.assertEqual(self.model.__class__.__name__, 'PtBertRerankModelPlugin')
        self.assertIsInstance(ranks, list)
        self.assertEqual(len(CHOICES), len(ranks))

    def test_filter(self):
        ranks, scores = self.model.rank('What is fish oil?', CHOICES, filter_results=True)
        self.assertEqual("EPA Fish Oil can be defined as fish oil that contains a high concentration   of EPA. EPA (Eicosapentaenoic Acid) and DHA (Docosahexaenoic Acid) are both   Omega 3 essential Fatty Acids, both of which are beneficial in their own right.   However, research has shown that EPA can be more effective, over time, when   there is less DHA to compete with it. Therefore, to be considered a high EPA   fish oil, we would want to see a much higher concentration of EPA than DHA.   There are some fish oils claiming EPA/DHA ratios in the region of 8 to 1, but   not many. Pure EPA fish oil, on the other hand, contains no DHA at all, and   as such, has an EPA concentration of 93%, arguably one of the strongest and most concentrated, high-grade EPA fish oils on the market today.",
                         CHOICES[ranks[0]])
        self.assertIsInstance(ranks, list)
        self.assertEqual(2, len(ranks))

        # ranks, scores = self.model.rank('His tender heir', CHOICES[:1], filter_results=True)
        # self.assertIsInstance(ranks, list)
        # self.assertEqual(0, len(ranks))

    def tearDown(self) -> None:
        self.model.close()


CHOICES = ['EPA Fish Oil can be defined as fish oil that contains a high concentration   of EPA. EPA (Eicosapentaenoic Acid) and DHA (Docosahexaenoic Acid) are both   Omega 3 essential Fatty Acids, both of which are beneficial in their own right.   However, research has shown that EPA can be more effective, over time, when   there is less DHA to compete with it. Therefore, to be considered a high EPA   fish oil, we would want to see a much higher concentration of EPA than DHA.   There are some fish oils claiming EPA/DHA ratios in the region of 8 to 1, but   not many. Pure EPA fish oil, on the other hand, contains no DHA at all, and   as such, has an EPA concentration of 93%, arguably one of the strongest and most concentrated, high-grade EPA fish oils on the market today.', 'Sustainable , Strong  Wild Fish Oil.', 'What Is Epa Fish Oil?', 'Pure EPA Fish Oil, Benefiting People All Over The World Since 2005.', '*Pure EPA is a powerful pharmaceutical grade omega 3 fish oil', '*A unique product containing the purest form of ethyl EPA fish oil in the UK', 'Surpasses International fish  oil standards', 'Doctor’s advice', 'Due to the overwhelming success of this special offer it will be extend until futher notice.', 'Testimonial', 'Strong , Clean, Premium  Effective', 'Results may vary, this is an individual testimonial.', '(Box of 60 capsules)', 'FREE newsletter, all the latest knowledge in health and lifestyle →', 'Pure EPA Essential Oil Blend', 'Postage & Packing\n\t\t\t\t\t\tMainland UK: \t£2.50 | Rest of EU: \t£3.00 | Rest of World: £3.50\n\t\t\t\t\t\tOrder 6 items or more: FREE delivery.', 'Essential oil Pure EPA is available exclusively from mind 1st.\n\t\t\t\t\t\t\tMind1st Information Line: 01772 877925', 'I think diet is the foundation for health. If somebody isn’t physically healthy ,then you can’t expect to be healthy. You actually need to have EPA molecules in order to get good membranes for your cells so they function properly. Read more about Dr Myers', 'I started taking pure EPA three months ago for my general health. I am pleased to report an interesting side effect following taking the EPA. Two months after starting to take it, I no longer have any period pain or PMS. I have suffered badly for 30 years and up until last month had always spent a few days in bed. Last month – nothing! Not a twinge, not an ache, not tired. That is the first time in my whole life I have had a problem free period.']