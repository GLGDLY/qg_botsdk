.. qg_botsdk documentation master file, created by
   sphinx-quickstart on Mon Aug 15 14:10:54 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

qg_botsdk 
==========

.. raw:: html

    <div align="center">

    <p><a target="_blank" rel="noopener noreferrer" href="https://camo.githubusercontent.com/21cd09e01e0a4b0f06d5425c750a59793fed9474b30e3c4047405a513b21ee2e/68747470733a2f2f736f6369616c6966792e6769742e63692f474c47444c592f71675f626f7473646b2f696d6167653f6465736372697074696f6e3d3126666f6e743d536f75726365253230436f646525323050726f26666f726b733d31266973737565733d31266c616e67756167653d31266c6f676f3d68747470732533412532462532466769746875622e636f6d25324674656e63656e742d636f6e6e656374253246626f742d646f6373253246626c6f622532466d61696e253246646f63732532462e76756570726573732532467075626c696325324666617669636f6e2d363470782e706e6725334672617725334474727565266e616d653d31266f776e65723d31267061747465726e3d466c6f6174696e67253230436f67732670756c6c733d31267374617267617a6572733d31267468656d653d4c69676874"><img src="https://camo.githubusercontent.com/21cd09e01e0a4b0f06d5425c750a59793fed9474b30e3c4047405a513b21ee2e/68747470733a2f2f736f6369616c6966792e6769742e63692f474c47444c592f71675f626f7473646b2f696d6167653f6465736372697074696f6e3d3126666f6e743d536f75726365253230436f646525323050726f26666f726b733d31266973737565733d31266c616e67756167653d31266c6f676f3d68747470732533412532462532466769746875622e636f6d25324674656e63656e742d636f6e6e656374253246626f742d646f6373253246626c6f622532466d61696e253246646f63732532462e76756570726573732532467075626c696325324666617669636f6e2d363470782e706e6725334672617725334474727565266e616d653d31266f776e65723d31267061747465726e3d466c6f6174696e67253230436f67732670756c6c733d31267374617267617a6572733d31267468656d653d4c69676874" alt="qg_botsdk" data-canonical-src="https://socialify.git.ci/GLGDLY/qg_botsdk/image?description=1&amp;font=Source%20Code%20Pro&amp;forks=1&amp;issues=1&amp;language=1&amp;logo=https%3A%2F%2Fgithub.com%2Ftencent-connect%2Fbot-docs%2Fblob%2Fmain%2Fdocs%2F.vuepress%2Fpublic%2Ffavicon-64px.png%3Fraw%3Dtrue&amp;name=1&amp;owner=1&amp;pattern=Floating%20Cogs&amp;pulls=1&amp;stargazers=1&amp;theme=Light" style="max-width: 100%;"></a></p>

    <p><a href="https://www.python.org/" rel="nofollow"><img src="https://camo.githubusercontent.com/758ca08b7c08aa13b1233dc1611176da96830cc1256dcea118acf9b09fa09887/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c616e67756167652d707974686f6e2d677265656e2e7376673f7374796c653d706c6173746963" alt="Language" data-canonical-src="https://img.shields.io/badge/language-python-green.svg?style=plastic" style="max-width: 100%;"></a>
    <a href="https://github.com/GLGDLY/qg_botsdk/blob/master/LICENSE"><img src="https://camo.githubusercontent.com/74431d882d9d06aa6b045791be8f005eaaf43a7b6f6aabb2bfb29f0bced8a63a/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d4d49542d6f72616e67652e7376673f7374796c653d706c6173746963" alt="License" data-canonical-src="https://img.shields.io/badge/license-MIT-orange.svg?style=plastic" style="max-width: 100%;"></a>
    <a href="https://github.com/GLGDLY/qg_botsdk/releases"><img src="https://camo.githubusercontent.com/36724ccce6d358d91703b7d529d86879f14b6cd55851a5576c4e98465bfff6f4/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f762f72656c656173652f474c47444c592f71675f626f7473646b3f7374796c653d706c6173746963" alt="Releases" data-canonical-src="https://img.shields.io/github/v/release/GLGDLY/qg_botsdk?style=plastic" style="max-width: 100%;"></a>
    <a href="https://pypi.org/project/qg-botsdk/" rel="nofollow"><img src="https://camo.githubusercontent.com/360de62d4dbcbe21b37202ed940ae211697f2663101fd65e4185f0369d6502ae/68747470733a2f2f696d672e736869656c64732e696f2f707970692f64772f71672d626f7473646b3f7374796c653d706c617374696326636f6c6f723d626c7565" alt="Pypi" data-canonical-src="https://img.shields.io/pypi/dw/qg-botsdk?style=plastic&amp;color=blue" style="max-width: 100%;"></a>
    <a href="https://www.codacy.com/gh/GLGDLY/qg_botsdk/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=GLGDLY/qg_botsdk&amp;utm_campaign=Badge_Grade" rel="nofollow"><img src="https://camo.githubusercontent.com/c57e2d6f30166c52115b085095308aa0bc323135797777eaaa6438c0b631da6d/68747470733a2f2f6170702e636f646163792e636f6d2f70726f6a6563742f62616467652f47726164652f6630313535343962336462613436303262653266653066356438623061386435" alt="Codacy Badge" data-canonical-src="https://app.codacy.com/project/badge/Grade/f015549b3dba4602be2fe0f5d8b0a8d5" style="max-width: 100%;"></a></p>

    ✨用于QQ官方频道机器人，兼顾实用与容易入门的Python应用级SDK✨

    <p><a href="https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b51" rel="nofollow">文档</a>
    ·
    <a href="https://github.com/GLGDLY/qg_botsdk/releases">下载</a>
    ·
    <a href="https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b52" rel="nofollow">快速入门</a></p>

    </div>

- 这里是 qg_botsdk 的 readthedocs 托管文档

- 注意另有 `thoughts 托管文档 <https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b51>`_ 可供查阅帮助文档内容

下载方式
^^^^^^^^

-   直接下载 `最新release <https://github.com/GLGDLY/qg_botsdk/releases>`_ ，放到项目中即可
-   pip安装（推荐）：

.. code-block:: bash

    pip install qg-botsdk

-------------------

.. toctree::
   :maxdepth: 2

   简介
   快速入门
   SDK组件
   API
   Model库
   常见问题Q&A
   联系与反馈
   qg_botsdk @Github <https://github.com/GLGDLY/qg_botsdk>
   qg_botsdk @Pypi <https://pypi.org/project/qg-botsdk/>
   机器人官方API文档 <https://bot.q.qq.com/wiki/develop/api/>
