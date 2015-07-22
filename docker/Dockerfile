FROM scratch
ADD buildout.nix.tar.gz /
ENV PATH=/app/bin CFLAGS=-I/app/include LDFLAGS=-L/app/lib
ENV SSL_CERT_FILE=/app/etc/ssl/certs/ca-bundle.crt
EXPOSE 8080
USER 1000
ENTRYPOINT ["/app/bin/buildout"]
