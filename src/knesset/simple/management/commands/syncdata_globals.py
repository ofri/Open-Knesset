# -*- coding: utf-8 -*-
import re
# defines for finding explanation part in private proposals
p_explanation = '</p><p class="explanation-header">דברי הסבר</p><p>'.decode('utf8')
strong_explanation = re.compile('<strong>\s*ד\s*ב\s*ר\s*י\s*ה\s*ס\s*ב\s*ר\s*</strong>'.decode('utf8'),re.UNICODE)
explanation = re.compile('ד\s*ב\s*ר\s*י\s*ה\s*ס\s*ב\s*ר'.decode('utf8'), re.UNICODE)
