-- OmniFocus 任务导出脚本
-- 导出今日和近期任务，包含完整元数据

tell application "OmniFocus 3"
	set taskList to {}
	set todayDate to current date
	set endOfTomorrow to todayDate + (48 * 60 * 60) - 1
	
	-- 获取今日和明日的任务
	repeat with aTask in (every flattened task of default document whose ((due date is not missing value and due date ≤ endOfTomorrow) or (defer date is not missing value and defer date ≤ todayDate)) and completed is false)
		
		set taskName to name of aTask
		set taskId to id of aTask as string
		set taskNote to note of aTask
		set taskFlagged to flagged of aTask
		set taskCompleted to completed of aTask
		
		-- 获取项目信息
		set taskProject to ""
		try
			set taskProject to name of containing project of aTask
		on error
			set taskProject to "Inbox"
		end try
		
		-- 获取上下文信息
		set taskContext to ""
		try
			set taskContext to name of context of aTask
		on error
			set taskContext to ""
		end try
		
		-- 获取时间信息
		set taskDue to ""
		try
			set taskDue to due date of aTask as string
		on error
			set taskDue to ""
		end try
		
		set taskDefer to ""
		try
			set taskDefer to defer date of aTask as string
		on error
			set taskDefer to ""
		end try
		
		-- 获取预估时间
		set taskEstimate to 0
		try
			set taskEstimate to estimated minutes of aTask
		on error
			set taskEstimate to 0
		end try
		
		-- 构建任务数据
		set taskData to {¬
			id:taskId, ¬
			name:taskName, ¬
			note:taskNote, ¬
			project:taskProject, ¬
			context:taskContext, ¬
			flagged:taskFlagged, ¬
			completed:taskCompleted, ¬
			dueDate:taskDue, ¬
			deferDate:taskDefer, ¬
			estimatedMinutes:taskEstimate}
		
		set end of taskList to taskData
	end repeat
	
	-- 转换为JSON格式
	set jsonOutput to my listToJSON(taskList)
	
	-- 保存到文件
	set outputFile to (path to home folder as string) & "LifeOS:data:omnifocus_export.json"
	set fileRef to open for access file outputFile with write permission
	set eof of fileRef to 0
	write jsonOutput to fileRef
	close access fileRef
	
	-- 显示结果
	display notification "已导出 " & (count of taskList) & " 个任务到 LifeOS" with title "OmniFocus Export" sound name "Glass"
	
	return jsonOutput
end tell

-- JSON转换函数
on listToJSON(taskList)
	set json to "["
	repeat with i from 1 to count of taskList
		set taskData to item i of taskList
		set json to json & "{"
		set json to json & "\"id\":\"" & (id of taskData) & "\","
		set json to json & "\"name\":\"" & my escapeJSON(name of taskData) & "\","
		set json to json & "\"note\":\"" & my escapeJSON(note of taskData) & "\","
		set json to json & "\"project\":\"" & my escapeJSON(project of taskData) & "\","
		set json to json & "\"context\":\"" & my escapeJSON(context of taskData) & "\","
		set json to json & "\"flagged\":" & (flagged of taskData) & ","
		set json to json & "\"completed\":" & (completed of taskData) & ","
		set json to json & "\"dueDate\":\"" & my escapeJSON(dueDate of taskData) & "\","
		set json to json & "\"deferDate\":\"" & my escapeJSON(deferDate of taskData) & "\","
		set json to json & "\"estimatedMinutes\":" & (estimatedMinutes of taskData)
		set json to json & "}"
		if i < count of taskList then set json to json & ","
	end repeat
	set json to json & "]"
	return json
end listToJSON

-- JSON字符串转义
on escapeJSON(str)
	set str to my replaceText(str, "\\", "\\\\")
	set str to my replaceText(str, "\"", "\\\"")
	set str to my replaceText(str, return, "\\n")
	set str to my replaceText(str, tab, "\\t")
	return str
end escapeJSON

-- 字符串替换函数
on replaceText(subject, find, replace)
	set prevTIDs to text item delimiters of AppleScript
	set text item delimiters of AppleScript to find
	set subject to text items of subject
	set text item delimiters of AppleScript to replace
	set subject to "" & subject
	set text item delimiters of AppleScript to prevTIDs
	return subject
end replaceText