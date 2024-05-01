'''
   Copyright 2012 Will Rogers

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

@author Will Rogers

Module containing the Loader object.
'''

from __future__ import absolute_import

# public interface for apel.dbloader

from .loader import Loader, LoaderException
from .car_parser import CarParser
from .aur_parser import AurParser
from .star_parser import StarParser
