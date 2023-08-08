"""
eğer test dosyası ana dizinden import yapamazsa bu dosyayı kullanabiliriz.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
