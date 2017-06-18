import YoutubeTutorial.modules.maths

print('Example 1:', YoutubeTutorial.modules.maths.add(5, 5, 3, 12))

import YoutubeTutorial.modules.maths as m

print('Example 2:', m.sub(5, 4))

from YoutubeTutorial.modules.maths import *
print('Example 3:', multi(3, 6, 5))

from YoutubeTutorial.modules.maths import div
print('Example 4:', div(5, 7))

from YoutubeTutorial.modules.maths import multi as m1, add as a
print('Example 5:', m1(1, 2, 3))
print('Example 6:', a(4, 6, 7))



