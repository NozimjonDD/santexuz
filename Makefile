deploy-dev:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 [go or manage.py] build -ldflags="-w -s" -o bin/dir cmd/myproject/main.service
	ssh myproject "systemctl stop gunicorn.service"
	scp bin/myproject "myproject:/var/www/myproject/api/bin"
	ssh myproject "systemctl start gunicorn.service"
