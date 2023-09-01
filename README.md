## 获取基础信息
|method|终结点|
|-|-|
|`get`|`/api/getbaseinfo`|
### 参数
|字段|类型|默认值|说明|
|-|-|-|-|
|无|无|无|无|
### 响应数据（Json）
|字段|类型|说明|
|-|-|-|
|`title`|`string`|网页显示标题|
|`datelist`|`string[]`|所有可以查询的日期|

## 获取昨日新增报错
|method|终结点|
|-|-|
|`get`|`/api/getresults`|
### 参数
|字段|类型|默认值|说明|
|-|-|-|-|
|`date`|`string`|` `|查询日期，格式为`YYYY-mm-DD`|
### 响应数据（Json）
|字段|类型|说明|
|-|-|-|
|`errorlist`|`errorlist[]`|静态检查警告列表|
### errorlist（Json）
|字段|类型|说明|
|-|-|-|
|`id`|`int`|唯一的编号|
|`level`|`string`|警告级别|
|`owner`|`string`|负责人|
|`file`|`string`|文件路径|
|`line`|`string`|行号|
|`date`|`string`|日期，格式为`YYYY-mm-DD`|
|`errortype`|`string`|错误类型|
|`errorinfo`|`string`|错误信息|
|`msg`|`string`|提示信息|
|`content`|`string`|出现问题的代码块|

## 获取当前全部报错
|method|终结点|
|-|-|
|`get`|`/api/getallresults`|
### 参数
|字段|类型|默认值|说明|
|-|-|-|-|
|无|无|无|无|
### 响应数据（Json）
|字段|类型|说明|
|-|-|-|
|`errorlist`|`errorlist[]`|静态检查警告列表|
### errorlist（Json）
|字段|类型|说明|
|-|-|-|
|`id`|`int`|唯一的编号|
|`level`|`string`|警告级别|
|`owner`|`string`|负责人|
|`file`|`string`|文件路径|
|`line`|`string`|行号|
|`date`|`string`|日期，格式为`YYYY-mm-DD`|
|`errortype`|`string`|错误类型|
|`errorinfo`|`string`|错误信息|
|`msg`|`string`|提示信息|
|`content`|`string`|出现问题的代码块|

## 设置负责人
|method|终结点|
|-|-|
|`get`|`/api/setowner`|
### 参数
|字段|类型|默认值|说明|
|-|-|-|-|
|`id`|`int`|` `|警告的编号|
|`owner`|`string`|` `|负责人|
### 响应数据（Json）
|字段|类型|说明|
|-|-|-|
|`isok`|`int`|1表示操作成功|
