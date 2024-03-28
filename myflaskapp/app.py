from flask import Flask, render_template
import boto3
import concurrent.futures
from datetime import datetime, timedelta

app = Flask(__name__)

cloudwatch_logs = boto3.client('logs')

def get_log_events(log_group, start_time, end_time):
    try:
        events = cloudwatch_logs.filter_log_events(
            logGroupName=log_group,
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000),
        )
        return events['events']
    except Exception as e:
        print(f"{log_group} 로그를 가져오는 중 오류가 발생했습니다: {e}")
        return []

def get_logs_from_multiple_groups(log_groups, start_time, end_time):
    all_events = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_log_group = {executor.submit(get_log_events, lg, start_time, end_time): lg for lg in log_groups}
        for future in concurrent.futures.as_completed(future_to_log_group):
            log_group = future_to_log_group[future]
            log_events = future.result()
            all_events.extend(log_events)
    return all_events

@app.route('/')
def home():
    log_groups = ['/aws/lambda/your-first-lambda-function-name', '/aws/lambda/your-second-lambda-function-name']
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()
    logs = get_logs_from_multiple_groups(log_groups, start_time, end_time)
    return render_template('/black-dashboard-master/examples/dashboard.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)


