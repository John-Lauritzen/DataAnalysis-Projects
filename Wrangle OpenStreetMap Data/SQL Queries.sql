SELECT count(*)
FROM [dbo].[nodes]

SELECT count(*)
FROM [dbo].[ways]

SELECT COUNT(DISTINCT(u.[uid]))          
FROM (SELECT [uid] FROM [dbo].[nodes] UNION ALL SELECT [uid] FROM [dbo].[ways]) u

SELECT [key], COUNT(*) as num
FROM [dbo].[nodes_tags]
GROUP BY [key]
ORDER BY num DESC

SELECT [value], count(*)
FROM [dbo].[nodes_tags]
WHERE [key] = 'religion'
GROUP BY [value]
ORDER BY 2 DESC

SELECT DISTINCT [id]
FROM [dbo].[nodes_tags]
WHERE [id] IN (SELECT [id] FROM [dbo].[nodes_tags] WHERE [key] = 'religion')
AND [key] != 'religion'

SELECT count(*), [key]
FROM [dbo].[nodes_tags]
WHERE [id] IN (SELECT DISTINCT [node_id] FROM [dbo].[ways_nodes])
GROUP BY [key]
ORDER BY 1 DESC

SELECT wt.[value], count(*)
FROM [dbo].[ways_tags] wt JOIN [dbo].[ways_nodes] wn ON wt.[id] = wn.[id]
WHERE wt.id IN (SELECT DISTINCT [id] FROM [dbo].[ways_tags] WHERE [key] = 'crossing')
AND wt.[key] = 'name'
GROUP BY wt.[value]
ORDER BY 2 DESC

SELECT *
FROM ways_tags
WHERE id IN (SELECT DISTINCT id FROM ways_tags WHERE [key] = 'name' AND [value] = 'Redwood Road')
AND [key] = 'crossing'

SELECT *
FROM 

SELECT count(*)
FROM ways_tags
WHERE type = 'tiger' AND [key] = 'reviewed' AND value = 'no'

SELECT count(*)
FROM ways_tags
WHERE [type] = 'hov' OR [key] = 'hov'