from peewee import *

from mobiglas.db import BaseModel, database

sql_create_status_trigger_1 = """ 
                                    CREATE TRIGGER IF NOT EXISTS motion_to_in_progress
                                        AFTER UPDATE
                                        ON motion
                                        WHEN new.status = 'IN_PROGRESS'
                                    BEGIN
                                        UPDATE motion SET
                                            start_time = datetime('now'),
                                            end_time = datetime('now', '+'||timeout||' hours');
                                    END; """

sql_create_status_trigger_2 = """ 
                                    CREATE TRIGGER IF NOT EXISTS motion_to_complete
                                        AFTER UPDATE
                                        ON motion
                                        WHEN new.status = 'COMPLETE'
                                    BEGIN
                                       UPDATE motion SET end_time = datetime('now');
                                    END; """

sql_create_status_trigger_3 = """ 
                                    CREATE TRIGGER IF NOT EXISTS motion_to_close
                                        AFTER UPDATE
                                        ON motion
                                        WHEN new.status = 'CLOSED'      
                                    BEGIN
                                        DELETE FROM motion WHERE new.status = 'CLOSED';
                                    END; """

sql_create_status_trigger_4 = """ 
                                    CREATE TRIGGER IF NOT EXISTS motion_to_reopen
                                        AFTER UPDATE
                                        ON motion
                                        WHEN new.status = 'NOT_STARTED' and old.status = 'TABLED'      
                                    BEGIN
                                        UPDATE motion SET tally_nay_count = 0, 
                                            tally_yea_count = 0,
                                            tally_yeas = null,
                                            tally_nays = null,
                                            tally_tabled_user = null;
                                    END; """

sql_create_tally_trigger_1 = """ 
                                    CREATE TRIGGER IF NOT EXISTS motion_tally_counter
                                        AFTER UPDATE
                                        ON motion
                                        WHEN NEW.tally_yea_count + NEW.tally_nay_count = OLD.eligible_max
                                    BEGIN
                                        UPDATE motion SET status = 'COMPLETE';
                                    END; """

sql_create_tally_trigger_2 = """ 
                                    CREATE TRIGGER IF NOT EXISTS motion_tally_tabled
                                        AFTER UPDATE
                                        ON motion
                                        WHEN NEW.tally_tabled_user is not null and OLD.status != 'TABLED'
                                    BEGIN
                                        UPDATE motion SET status = 'TABLED';
                                    END; """


class Motion(BaseModel):
    id = BigIntegerField(unique=True, primary_key=True, help_text='discord.channel_id')
    name = TextField(null=True)
    status = TextField(default='NOT_STARTED', help_text='[NOT_STARTED, IN_PROGRESS, TABLED, COMPLETE, CLOSED]')
    creator_id = TextField()
    detail_id = BigIntegerField(null=True)
    start_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    end_time = DateTimeField(null=True)
    timeout = SmallIntegerField(default=24)
    motion_id = BigIntegerField(null=True)
    eligible_members = TextField()
    eligible_max = SmallIntegerField()
    tally_yeas = TextField(null=True)
    tally_yea_count = SmallIntegerField(default=0)
    tally_nays = TextField(null=True)
    tally_nay_count = SmallIntegerField(default=0)
    tally_tabled_user = TextField(null=True)


# setup
database.create_tables(models=[Motion])

database.execute_sql(sql=sql_create_status_trigger_1, commit=True)
database.execute_sql(sql=sql_create_status_trigger_2, commit=True)
database.execute_sql(sql=sql_create_status_trigger_3, commit=True)
database.execute_sql(sql=sql_create_status_trigger_4, commit=True)
database.execute_sql(sql=sql_create_tally_trigger_1, commit=True)
database.execute_sql(sql=sql_create_tally_trigger_2, commit=True)
