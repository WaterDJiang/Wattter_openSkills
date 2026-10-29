/* WTT file wrapper; SHA-256 comes from the pinned MuPDF crypt-sha2.c. */
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include "mupdf/fitz.h"

/* WTT Base64 decoder. Only decoding is exposed to the bootstrap script. */
static int decode_base64(void)
{
    const char *alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    int c, q[4], used=0, ended=0;
    while ((c=getchar()) != EOF) {
        if (isspace((unsigned char)c)) continue;
        if (ended) goto bad;
        const char *p = c ? strchr(alphabet,c) : NULL;
        if (c!='=' && !p) goto bad;
        q[used++]=c=='=' ? 64 : (int)(p-alphabet);
        if (used!=4) continue;
        if(q[0]==64 || q[1]==64 || (q[2]==64 && q[3]!=64)) goto bad;
        if((q[2]==64 && (q[1]&15)) || (q[3]==64 && q[2]!=64 && (q[2]&3))) goto bad;
        unsigned char out[3]={(unsigned char)((q[0]<<2)|(q[1]>>4)),
            (unsigned char)((q[1]<<4)|(q[2]>>2)),(unsigned char)((q[2]<<6)|q[3])};
        size_t n=q[2]==64 ? 1 : q[3]==64 ? 2 : 3;
        if (fwrite(out,1,n,stdout)!=n) return 3;
        ended=q[3]==64;used=0;
    }
    if(used || ferror(stdin)) goto bad;
    return fflush(stdout)==0 ? 0 : 3;
bad:
    fputs("wtt-tools: invalid Base64 input\n",stderr);return 3;
}

int main(int argc, char **argv)
{
    const char *name=strrchr(argv[0],'/');name=name?name+1:argv[0];
    if(!strcmp(name,"base64")) {
        if(argc!=2 || (strcmp(argv[1],"-d") && strcmp(argv[1],"--decode"))) {
            fputs("usage: base64 -d\n",stderr);return 2;
        }
        return decode_base64();
    }
    if (argc != 2) { fputs("usage: wtt-sha256 FILE\n", stderr); return 2; }
    FILE *file = fopen(argv[1], "rb");
    if (!file) { perror("wtt-sha256"); return 3; }
    fz_sha256 state;
    unsigned char buffer[16384], hash[32];
    fz_sha256_init(&state);
    size_t n;
    while ((n = fread(buffer, 1, sizeof buffer, file)) != 0)
        fz_sha256_update(&state, buffer, n);
    int failed = ferror(file);
    if (fclose(file) != 0) failed = 1;
    if (failed) { fputs("wtt-sha256: file read failed\n", stderr); return 3; }
    fz_sha256_final(&state, hash);
    for (size_t i = 0; i < sizeof hash; ++i) printf("%02x", hash[i]);
    putchar('\n');
    return 0;
}
