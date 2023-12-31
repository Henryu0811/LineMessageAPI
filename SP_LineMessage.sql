USE [dbDATABASE]
GO
/****** Object:  StoredProcedure [dbo].[SP_LineMessage]    Script Date: 2023/9/20 下午 05:29:46 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER    PROCEDURE [dbo].[SP_LineMessage]
as

begin

	declare @cmd nvarchar(1000), @filename char(8)

	drop table if exists TB_temp
	create table TB_temp(c1 varchar(100))

	set @filename = convert(char(8), getdate(), 112)
	select @filename


	set @cmd = '
	bulk insert dbDATABASE.dbo.TB_temp from ''D:\LineMessage\'+ @filename +'.txt''
	with (
		datafiletype = ''char'',
		codepage = ''65001''
	)
	'
	exec sp_executesql @cmd

	exec sp_configure 'show advanced options', 1
	reconfigure
	exec sp_configure 'xp_cmdshell', 1
	reconfigure

	set @cmd = N'EXEC xp_cmdshell ''del D:\LineMessage\' + @filename + '.txt''';
	exec sp_executesql @cmd;


	declare @value nvarchar(1000), @CRUD varchar(10), @application varchar(10)

	set @value = (select * from TB_temp)
	set @CRUD = (select substring(c1, 14, 2) from TB_temp)
	set @application = (select substring(c1, 17, 2) from TB_temp)

	if (@CRUD = '新增')
	begin

		if (@application = '記帳')
		begin

			drop table if exists tb_split
			select value, row_number() over(order by (select null)) as rnk
			into tb_split
			from string_split(@value, '/')

			insert into tLine_istxn
			select
				max(case when rnk=1 then value end) as iID,
				max(case when rnk=4 then value end) as iDate,
				max(case when rnk=5 then value end) as iType,
				max(case when rnk=6 then value end) as iDescription,
				max(case when rnk=7 then value end) as iAmount,
				max(case when rnk=8 then left(value,5)+'*****'+right(value,5) end) as iUser
			from tb_split

			drop table if exists tb_split

		end
		else if (@application = '健身')
		begin
			
			drop table if exists tb_split
			select value, row_number() over(order by (select null)) as rnk
			into tb_split
			from string_split(@value, '/')
			
			insert into tExercise
			select
				max(case when rnk=4  then value end) as fEX_DATE,
				max(case when rnk=5  then value end) as fEX_TYPE,
				max(case when rnk=6  then value end) as fEX_MUSCLE,
				max(case when rnk=7  then value end) as fEX_METHOD,
				max(case when rnk=8  then value end) as fEX_TIMES,
				max(case when rnk=9  then value end) as fEX_KG,
				max(case when rnk=10 then value end) as fEX_SETS,
				max(case when rnk=11 then value end) as fEX_UserID
			from tb_split

			drop table if exists tb_split

		end

	end

	if (@CRUD = '刪除')
	begin
	
		if (@application = '記帳')
		begin

			drop table if exists tb_split
			select value, row_number() over(order by (select null)) as rnk
			into tb_split
			from string_split(@value, '/')

			delete tLine_istxn
			where iID = (select	max(case when rnk=4 then value end) from tb_split)

			drop table if exists tb_split

		end
		else if (@application = '健身')
		begin
			
			drop table if exists tb_split
			select value, row_number() over(order by (select null)) as rnk
			into tb_split
			from string_split(@value, '/')

			delete tExercise
			where fEX_DATE	= (select max(case when rnk=4  then value end) from tb_split)
			and fEX_TYPE	= (select max(case when rnk=5  then value end) from tb_split)
			and fEX_MUSCLE	= (select max(case when rnk=6  then value end) from tb_split)
			and fEX_METHOD	= (select max(case when rnk=7  then value end) from tb_split)
			and fEX_TIMES	= (select max(case when rnk=8  then value end) from tb_split)
			and fEX_KG		= (select max(case when rnk=9  then value end) from tb_split)
			and fEX_SETS	= (select max(case when rnk=10 then value end) from tb_split)
			and fEX_UserID	= (select max(case when rnk=11 then value end) from tb_split)

			drop table if exists tb_split

		end

	end

end