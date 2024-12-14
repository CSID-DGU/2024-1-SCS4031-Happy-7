## OBservator Server
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)

### 관련 링크 (바로가기)
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/CSID-DGU/2024-2-SCS4031-Happy-7)
[![Amazon S3](https://img.shields.io/badge/Amazon%20S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white)
](https://observator-s3.s3.amazonaws.com)

### 서버 구조 (트리)
```
/home/ubuntu/project
├── codes
│   ├── etc
│   └── main
├── data
│   ├── csv
│   │   ├── orderbooks
│   │   └── ticks
│   ├── key
│   ├── queue
│   └── raw
│       ├── orderbooks
│       └── ticks
└── logs
    ├── crontab.log
    └── date
```

### Crontab (자동화)
```
0 0 * * * /usr/bin/python3 /home/ubuntu/project/codes/etc/delete.py >> /home/ubuntu/project/logs/crontab.log 2>&1

1 0 * * * /home/ubuntu/anaconda3/envs/venv/bin/python /home/ubuntu/project/codes/etc/csv_convert.py >> /home/ubuntu/project/logs/crontab.log 2>&1

5 0 * * * /home/ubuntu/anaconda3/envs/venv/bin/python /home/ubuntu/project/codes/etc/s3_upload.py >> /home/ubuntu/project/logs/crontab.log 2>&1
```
