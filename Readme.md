## To build a docker image with our selenium script
```
docker build --build-arg username=<USERNAME> --build-arg password=<PASSWORD> --build-arg notifip=<IP_ADDRESS> -t shops_schedule .
```
## To run via docker container
```
docker run -ti --rm shops_schedule
```

## To Schedule inside cron add the following line to cron to run every hour
```
0 */1 * * * docker run -d --rm shops_schedule
```
