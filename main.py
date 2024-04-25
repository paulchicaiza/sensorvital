import vital_sensor_decode
from datetime import datetime, time

from app_config import CustomLogger

logger = CustomLogger('main')

if __name__ == '__main__':
    try:
        start_date = datetime.combine(datetime.now(), time(0, 0, 0))
        #messages = vital_sensor_decode.get_messages(start_date=start_date)
        #vital_sensor_decode.print_decode_messages(messages)
        response = vital_sensor_decode.process_json_message()
        #vital_sensor_decode.print_decode_messages(response)
        vital_sensor_decode.save_messages_csv(response)
        #for message_data in response:
            #for message in message_data.message_values:
                #print(message.date, "" ,message.values)
    except Exception as e:
        logger.error(e)